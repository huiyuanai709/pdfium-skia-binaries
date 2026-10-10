# pdfium-skia-binaries

基于 [paulocoutinhox/pdfium-lib](https://github.com/paulocoutinhox/pdfium-lib)（上游提交 `f2bed3c8bd49569a6b5c2a0df3a1ae0def3d8871`）的独立构建仓库。只为 Linux x64 产出一份带 Skia 的 `libpdfium.so`，给 miniocr 替换旁边那份库。本仓库不并进 miniocr。

构建脚本是 MIT，版权在 [LICENSE.md](LICENSE.md)（Copyright (c) 2018-2026 Paulo Coutinho）。PDFium 和 Skia 的许可证在检出的源码里，不在本仓库。

钉的修订是 PDFium `chromium/8066`，和 NuGet `bblanchon.PDFium` 156.0.8066 同一修订，这样现有的 `FPDF_LIBRARY_CONFIG` version 4（64 位上 48 字节）不用改。GN 同时打开 `pdf_use_skia=true` 和 `pdf_use_agg=true`，进程启动时用 `m_RendererType` 二选一。V8 和 XFA 关闭。

## 下载产物

公开仓库的 Actions 跑完后，artifact 名是 `libpdfium-skia-linux-x64`，里面有：

- `libpdfium.so`
- `libpdfium.so.sha256`
- `symbols.txt`（`nm -D` 的结果，必须有 `FPDF_RenderPageSkia`，另外还有 `FPDF_InitLibraryWithConfig` 和 `FPDF_RenderPageBitmap`）

同一次 run 里还有 `linux-zip`（头文件加 `lib/x64/libpdfium.so`）。换 miniocr 只需要上面那份 `libpdfium.so`。

打开本仓库的 Actions，选最近一次成功的 **Linux Skia**，下载 artifact。命令行：

```bash
gh run download <run-id> -R huiyuanai709/pdfium-skia-binaries -n libpdfium-skia-linux-x64
sha256sum -c libpdfium.so.sha256
```

产物保留 14 天。默认不会发 Release。workflow 里的 `publish_release` 默认是关的。

## 换进 miniocr

1. 找到和现有 `libpdfium.so` 同一层的目录。比赛环境是 Native AOT 的 MiniOcr 目录，文件名必须仍叫 `libpdfium.so`。
2. 用下载的文件替换它。不要把这份 so 提交进 git，它比原来约 7.5MB 的 AGG 库大很多。
3. 启动时设置 `MINIOCR_PDF_RENDERER=skia`。这会写成 `PDFTOIMAGE_RENDERER=skia`。并行渲染进程是同一个二进制，会加载同一份 so，并继承这个环境变量。
4. 看 `/health`：`pdfRenderer` 应为 `skia`，`pdfSkiaBuild` 为 true。若这份 so 没有 `FPDF_RenderPageSkia`，程序会退回 AGG，不会去调会直接崩溃的 Skia 初始化。
5. 像素仍走 `FPDF_RenderPageBitmap`（Gray8 或 BGRA）。这是 CPU 位图，不是 GPU Surface。不要把 SkiaSharp 的 `SKCanvas` 传进 `FPDF_RenderPageSkia`，两边的 Skia ABI 不是同一份。
6. Skia 画出来的页不必和 AGG 逐字节相同。对比时开两个进程，各带各的环境变量。

单文件、非 AOT 的发布会把原生库解到 `$HOME/.net/MiniOcr/<hash>/`。那种布局要换解压后的那份，比赛路径用的是 AOT 目录。

这份 so 按系统 `libstdc++` 链接（`use_custom_libcxx=false`），用的是 Chromium 的 sysroot，glibc 要求保持在上游 pdfium-lib 那一档。换上去之后可以用 `ldd libpdfium.so` 看还缺不缺系统库。

## 这次 Actions 怎么编

- Runner 钉 **公开仓库** 的 `ubuntu-24.04`：4 vCPU、16 GB 内存。公开 4 核机器的磁盘通常有几十 GB 空闲，比文档里写的 14 GB 下限大。私有仓库的 `ubuntu-latest` 是 2 vCPU、8 GB 内存、大约 14 GB 磁盘，编不动，所以这个仓库保持公开。
- `symbol_level=0`，`NINJA_JOBS` 默认 **2**。可用内存低于约 12 GB 时，workflow 会加一块 8 GB 的 swap。空闲磁盘低于 40 GB 会清掉预装的 Android / .NET / GHC 等 SDK，**不会删 swap**；清完仍低于 25 GB 就失败退出。
- 单 job 超时 360 分钟。不带 Skia 的 linux-x64 大约几分钟到十几分钟；带上 Skia 之后按 45–120 分钟估，以这次 run 的实际时间为准。
- 公开仓库用标准 runner 不另收费。更大的 runner（8 核大约 $0.022/分钟，32 GB 内存）要 GitHub Team 或 Enterprise，而且标签得先在账号里存在。内存或链接被杀掉时，用 Actions 的 **Run workflow**，把 `runner` 改成那个标签（例如 `ubuntu-latest-8-cores`），`ninja_jobs` 降到 `1`。也可以在自备的 32 GB 内存、40 GB 以上磁盘的机器上跑下面的本地步骤。
- Actions cache 上限 10 GB，装不下这次 checkout，所以不缓存源码树。`depot_tools` 相对 `gclient sync` 很便宜。

`workflow_dispatch` 只有 workflow 文件在默认分支 `main` 上才能在网页上点。本仓库直接推 `main`，push 就会开编。iOS、Android、macOS、Windows、WASM 的 workflow 改成了只能手动点，避免一次 push 把那些平台也拉起来。

## 本地同样的步骤

不要在内存只有十几 GB 空闲、磁盘紧张的机器上跑完整链接。

```bash
python3 -m pip install -r requirements.txt
python3 make.py build-depot-tools
export PATH="$PWD/build/depot-tools:$PATH"
export NINJA_JOBS=2
python3 make.py build-pdfium-linux
python3 make.py patch-linux
python3 make.py build-linux
python3 make.py install-linux
nm -D build/linux/release/lib/x64/libpdfium.so | grep FPDF_RenderPageSkia
```

`build-pdfium-linux` 用 `checkout_configuration=small`。`minimal` 会跳过 `third_party/skia`，缺了目录会直接失败。补丁做两件事：把 `component("pdfium")` 改成 `shared_library("pdfium")`，并拿掉 `public/fpdfview.h` 里 `FPDF_EXPORT` 的 `COMPONENT_BUILD` 守卫。`is_component_build=false` 时如果不改头文件，`nm -D` 看不到 `FPDF_RenderPageSkia`。共享库不设 `pdf_is_complete_lib`。

装好的文件在 `build/linux/release/lib/x64/libpdfium.so`，install 时已经 `strip --strip-unneeded`。

示例用的大体积二进制（两个 logo、wasm 示例 PDF、约 14MB 的苹果示例 PDF）没有放进这个仓库，Linux 构建用不到。`sample/assets/f1.pdf` 是一页最小 PDF，只为让 `make.py test-linux` 能打开文件。上游原件在 paulocoutinhox/pdfium-lib 的同一路径。
