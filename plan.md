# Lab Completion Plan: AI Agent Cloud Deployment

## 1. Localhost vs Production
- [x] Đọc app.py ở 01-localhost-vs-production/develop, liệt kê 5 anti-patterns
- [x] Chạy thử app basic, test với curl
- [x] So sánh app.py basic và production, điền bảng so sánh
- [x] Hiểu về config, health check, logging, shutdown

## 2. Docker Containerization
- [x] Đọc Dockerfile ở 02-docker/develop, trả lời 4 câu hỏi
- [x] Build và run image, test với curl
- [x] Đọc Dockerfile multi-stage ở production, so sánh image size
- [x] Đọc docker-compose.yml, vẽ sơ đồ kiến trúc
- [x] Chạy docker compose up, test health và agent endpoint

## 3. Cloud Deployment
- [x] Deploy lên Railway (Thực tế): Đã có URL https://quoc-production.up.railway.app
- [x] Test public URL: Đã hoạt động với endpoint /health
- [x] (Optional) Đọc cloudbuild.yaml, service.yaml của GCP Cloud Run: Đã hiểu cơ chế IaC qua render.yaml

## 4. API Security
- [ ] Đọc app.py ở 04-api-gateway/develop, xác định API key check ở đâu
- [ ] Test API key đúng/sai với curl
- [ ] Đọc auth.py ở production, hiểu JWT flow, lấy token, test với token
- [ ] Đọc rate_limiter.py, xác định thuật toán, limit, bypass
- [ ] Test rate limit với for loop curl
- [ ] Đọc cost_guard.py, implement check_budget, test vượt budget

## 5. Scaling & Reliability
- [ ] Implement /health và /ready endpoint
- [ ] Implement graceful shutdown (signal handler)
- [ ] Refactor code thành stateless (state trong Redis)
- [ ] Chạy docker compose up --scale agent=3, test load balancing
- [ ] Test stateless bằng script test_stateless.py

## 6. Final Project
- [ ] Tạo project structure như hướng dẫn
- [ ] Implement config, main app, auth, rate limiter, cost guard
- [ ] Viết Dockerfile multi-stage, docker-compose.yml
- [ ] Test local với docker compose up --scale agent=3
- [ ] Deploy lên Railway/Render, set env, test public URL
- [ ] Chạy check_production_ready.py để kiểm tra

---

## Checklist (Tổng hợp)
- [ ] Hiểu sự khác biệt dev vs production
- [ ] Containerize app với Docker
- [ ] Deploy lên cloud platform
- [ ] Bảo mật API (API key/JWT)
- [ ] Implement rate limiting
- [ ] Implement cost guard
- [ ] Health check & readiness endpoint
- [ ] Graceful shutdown
- [ ] Stateless design (Redis)
- [ ] Structured logging
- [ ] Load balancing (Nginx)
- [ ] Public URL hoạt động
- [ ] Đạt đủ tiêu chí check_production_ready.py

---

## Ghi chú
- Đọc kỹ từng phần trong CODE_LAB.md trước khi làm
- Đánh dấu checklist khi hoàn thành từng bước
- Nếu gặp lỗi, xem TROUBLESHOOTING.md hoặc hỏi instructor
- Nên làm từng phần, test kỹ trước khi chuyển sang phần tiếp theo
