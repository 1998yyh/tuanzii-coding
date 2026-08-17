from __future__ import annotations

import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .reports import REPORT_ID_RE, load_reports, report_by_id
from .validation import validation_payload


COOKIE_NAME = "e2e_flow_center_session"


def _environment() -> tuple[Path, str]:
    project = Path(os.environ["E2E_FLOW_CENTER_PROJECT"]).resolve()
    token = os.environ["E2E_FLOW_CENTER_TOKEN"]
    return project, token


def create_app() -> FastAPI:
    project_root, token = _environment()
    dashboard_root = Path(__file__).resolve().parents[2]
    static_dir = dashboard_root / "static"
    app = FastAPI(title="E2E Flow Center", docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def authorized(request: Request) -> None:
        supplied = request.cookies.get(COOKIE_NAME) or request.headers.get("X-E2E-Flow-Center-Token", "")
        if not hmac.compare_digest(supplied, token):
            raise HTTPException(status_code=403, detail="当前会话未获授权。请使用启动命令输出的 URL。")

    def page_response(request: Request, access_token: str | None, redirect_url: str) -> FileResponse | RedirectResponse:
        # Exchange a one-time URL token for an HttpOnly session cookie, then serve the page.
        if access_token and hmac.compare_digest(access_token, token):
            response = RedirectResponse(url=redirect_url, status_code=303)
            response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="strict", secure=False)
            return response
        if not hmac.compare_digest(request.cookies.get(COOKIE_NAME, ""), token):
            raise HTTPException(status_code=403, detail="当前会话未获授权。请使用启动命令输出的 URL。")
        return FileResponse(static_dir / "index.html")

    @app.get("/", include_in_schema=False)
    def page(request: Request, access_token: str | None = Query(default=None, alias="token")):
        return page_response(request, access_token, "/")

    @app.get("/reports/extraction", include_in_schema=False)
    def report_page(request: Request, access_token: str | None = Query(default=None, alias="token"), report: str | None = None):
        # Preserve a direct report link while using the same token-to-cookie exchange as the home route.
        suffix = f"?report={report}" if report else ""
        return page_response(request, access_token, f"/reports/extraction{suffix}")

    @app.get("/api/health")
    def health(_: None = Depends(authorized)):
        payload = validation_payload(project_root)
        return {
            "status": "ok",
            "projectName": project_root.name,
            "validFlowCount": payload["validFlowCount"],
            "invalidFlowCount": payload["invalidFlowCount"],
        }

    @app.get("/api/flows")
    def flows(_: None = Depends(authorized)):
        return validation_payload(project_root)

    @app.get("/api/extraction-reports")
    def extraction_reports(_: None = Depends(authorized)):
        records = load_reports(project_root)
        return {
            "validReportCount": sum(record.valid for record in records),
            "invalidReportCount": sum(not record.valid for record in records),
            "reports": [record.listing() for record in records],
        }

    @app.get("/api/extraction-reports/{report_id}")
    def extraction_report(report_id: str, _: None = Depends(authorized)):
        if not REPORT_ID_RE.fullmatch(report_id):
            raise HTTPException(status_code=400, detail="report id 格式不合法。")
        record = report_by_id(project_root, report_id)
        if record is None:
            raise HTTPException(status_code=404, detail="报告不存在。")
        if not record.valid:
            raise HTTPException(status_code=422, detail={"filename": record.filename, "errors": record.errors})
        return record.document

    return app
