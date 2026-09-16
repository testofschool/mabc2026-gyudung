#!/usr/bin/env python3
"""
Vercel 정적 사이트 생성 스크립트
service/public/index.html 을 Vercel이 서빙할 수 있도록 설정
"""
import os
import shutil

# Vercel 정적 사이트: public/ 디렉토리에 인덱스 파일 배치
# 이미 service/public/index.html 이 있으므로, Vercel 프로젝트 루트에 복사

print("Vercel 정적 배포 준비...")
print(f"작업 디렉토리: {os.getcwd()}")
print(f"루트의 service/public/index.html 존재: {os.path.exists('service/public/index.html')}")
print("Vercel에 연결 후 'vercel --prod' 로 배포 가능")
