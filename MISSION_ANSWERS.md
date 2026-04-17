# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key hardcoded trong code (không dùng biến môi trường)
2. Port server cố định, không linh hoạt
3. Debug mode bật trong production
4. Không có endpoint health check
5. Không xử lý graceful shutdown (dừng server đột ngột)

### Exercise 1.3: Comparison table
| Feature      | Develop      | Production   | Why Important?                |
|--------------|-------------|-------------|-------------------------------|
| Config       | Hardcode    | Env vars    | Dễ thay đổi, bảo mật hơn      |
| Health check | Không có    | Có          | Giúp kiểm tra trạng thái app  |
| Logging      | print()     | JSON logging| Dễ đọc log, tích hợp hệ thống |
| Shutdown     | Đột ngột    | Graceful    | Không mất dữ liệu, ổn định    |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11 (basic), python:3.11-slim (production)
2. Working directory: /app
3. COPY requirements.txt trước để tận dụng cache layer, khi code thay đổi mà requirements không đổi thì không cần cài lại dependencies.
4. CMD là lệnh mặc định khi container start, ENTRYPOINT là entrypoint cố định không bị override bởi docker run.

### Exercise 2.3: Image size comparison
- Develop: ~1.6 GB (python:3.11)
- Production: ~424 MB (python:3.11-slim, multi-stage)
- Difference: Giảm ~70% nhờ multi-stage build, chỉ mang theo những gì cần thiết cho runtime.

