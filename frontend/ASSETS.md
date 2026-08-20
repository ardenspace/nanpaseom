# placeholder 에셋 홈 — `public/assets/`

디자이너가 `frontend/public/assets/` 에 **같은 파일명으로 덮어쓰기** 하는 드롭인 디렉토리.
Vite 빌드 시 `dist/assets/` 로 그대로 복사되어 `/assets/<name>` 으로 서빙된다.

이 안내문이 `public/assets/` 안이 아니라 여기 있는 이유: `public/` 의 파일은
빌드마다 `dist/` 로 그대로 복사되므로, 문서를 그 안에 두면 배포 산출물에 섞인다.

파일명 규약 (코드가 이 이름을 참조하므로 이름 변경 금지):

| 파일 | 용도 |
|---|---|
| `surigong.png` | 수리공 스프라이트 |
| `bg.png` | 배경 (어둑한 바다/난파섬) |
