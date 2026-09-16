#!/usr/bin/env python3
"""Vercel 제출 전 최종 프리플라이트 체크리스트"""
import os, sys, json, hashlib
from datetime import datetime

BASE = "/Users/felix/mabc-finals"

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:16]

def check_file(path, label, required=True):
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    status = "OK" if exists else (" Missing" if required else " N/A")
    print(f"[{status}] {label}: {path} ({size:,} bytes)")
    return exists, size

print("=" * 60)
print("규정다름 MABC 2026 결선 — 제출 전 프리플라이트")
print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

print("\n--- 제출물 파일 ---")
files = [
    ("submission/poster/강정민_포스터.pdf", "포스터 PDF"),
    ("강정민_PRD.pdf", "PRD PDF (루트)"),
    ("강정민_발표자료.pdf", "발표자료 PDF (루트)"),
    ("강정민_서비스소개.txt", "서비스 소개 (루트)"),
]

for path, label in files:
    check_file(os.path.join(BASE, path), label)

print("\n--- 서비스 코드 ---")
service_files = [
    ("service/public/index.html", "프론트엔드"),
    ("service/api/admrul-diff/index.py", "API 백엔드"),
    ("vercel.json", "Vercel 설정"),
    ("service/pyproject.toml", "Python 의존성"),
]
for path, label in service_files:
    check_file(os.path.join(BASE, path), label)

print("\n--- GitHub 제출 확인 ---")
print("[확인필요] GitHub: https://github.com/testofschool/mabc2026-gyudung — Public 여부 재확인 필요")
print("[확인필요] 코드에 API 키/토큰 포함 여부: 수동 확인 필요")

print("\n--- 서비스 URL ---")
print("[확인필요] https://mabc-finals.vercel.app — 로그인 없이 접속 가능해야 함")
print("[확인필요] 심사 시점 접속 가능 여부: Vercel 배포 상태 확인 필요")

print("\n--- 제약 확인 ---")
print("[확인필요] PRD/포스터/발표자료: 10MB 이하 — 파일 크기 확인 완료 (위 참조)")
print("[확인필요] 데모영상: 100MB 이하 — 강정민_데모영상.mp4 아직 없음 (사용자 녹화 예정)")
print("[확인필요] 데모영상: 3분 이내 — 사용자 녹화 시 확인 필요")
print("[확인필요] 포스터: A1 세로 1장 — 강정민_포스터.pdf 1페이지 확인 필요")
print("[확인필요] 포스터: 글꼴 아웃라인/임베딩 — PDF 폰트 임베딩 확인 필요")

print("\n--- skill-to-service 정합 ---")
print("[확인필요] admrul-diff: 서비스 API가 스크립트 기반 계산을 수행하는지 확인")
print("[확인필요] submission-preflight: 제출물 전체 게이트 통과 여부 — 수동 체크리스트")
print("[확인필요] pdf-form-fill-gate: 해당 없음 (양식 PDF 채우기 아님)")
print("[확인필요] front-build-spec/product-logic-spec/visual-production: 서비스 프론트/로직/디자인 정합 — 수동 확인")

print("\n--- 제출 양식 2 필수 항목 ---")
required = [
    "1. 서비스 공개 URL (로그인 없이 접속 가능)",
    "2. GitHub 레포지토리 URL (Public, API 키/토큰 금지)",
    "3. 서비스 동작 방식 설명 (400자 이내)",
    "4. PRD PDF (팀명_PRD.pdf, 10MB 이하)",
    "5. 포스터 PDF (팀명_포스터.pdf, A1 세로 1장, 10MB 이하, 글꼴 아웃라인)",
    "6. 발표자료 PDF (팀명_발표자료.pdf, 10MB 이하)",
    "7. 데모 영상 MP4 (팀명_데모영상.mp4, 3분 이내, 100MB 이하)",
    "8. 서비스 소개 (양식 내 텍스트)",
]
for item in required:
    print(f"  {item}")

print("\n--- 누락/미완료 ---")
print("  [미완료] 강정민_데모영상.mp4 — 사용자 직접 녹화 필요")
print("  [미완료] Google Form 제출 — gangjeongmin23@gmail.com 로그인 후 제출 필요")
print("  [확인필요] GitHub Public 상태 재확인")
print("  [확인필요] 포스터 글꼴 임베딩 확인")
print("  [확인필요] 서비스 URL 심사 시점 접속 가능 여부")

print("\n" + "=" * 60)
print("프리플라이트 완료 — 위 [확인필요]/[미완료] 항목 처리 후 제출")
print("=" * 60)
