# BBDown-UI

一个基于Python的UI界面封装BBDown命令方便使用，使用PySide6封装界面，跨平台，界面现代化一点，全局使用高级的毛玻璃效果，要注意色彩搭配。

## 功能特点

- 图形化界面操作，无需记忆复杂命令
- 支持多种API模式（默认/TV端/APP端/国际版）
- 可自定义视频编码和画质优先级
- 支持多种下载选项（仅视频、仅音频、弹幕等）
- 支持自定义文件命名规则
- 实时显示命令执行输出

## 安装和运行

### 环境要求

- Python 3.13+
- PySide6
- BBDown程序（需要单独下载并配置到系统PATH中）

### 安装依赖

```bash
# 使用uv安装（推荐）
uv sync

```

### 运行程序

```bash
python main.py
```

### 打包说明

```shell
nuitka \
  --macos-create-app-bundle \
  --macos-app-mode=gui \
  --standalone \
  --show-memory \
  --enable-plugin=pyside6 \
  --include-package-data=pyyaml \
  --show-progress \
  --output-dir=o \
  main.py

```

## 使用说明

1. 在输入框中输入哔哩哔哩视频地址或BV号
2. 根据需要选择下载选项
3. 点击"开始下载"按钮执行下载
4. 点击"仅解析信息"按钮查看视频信息而不下载
5. 点击"登录账号"按钮登录以下载会员内容

## 界面预览

（此处可添加界面截图）

## 开发说明

项目结构：
```
BBDown-UI/
├── main.py          # 主程序文件
├── README.md        # 说明文档
├── pyproject.toml   # 项目配置文件
└── uv.lock          # 依赖锁定文件
```

### BBDown原生命令行参考

> 仓库：https://github.com/nilaoda/BBDown.git

```bash
Description:
  BBDown是一个免费且便捷高效的哔哩哔哩下载/解析软件.

Usage:
  BBDown <url> [command] [options]

Arguments:
  <url>  视频地址 或 av|bv|BV|ep|ss

Options:
  -tv, --use-tv-api                              使用TV端解析模式
  -app, --use-app-api                            使用APP端解析模式
  -intl, --use-intl-api                          使用国际版(东南亚视频)解析模式
  --use-mp4box                                   使用MP4Box来混流
  -e, --encoding-priority <encoding-priority>    视频编码的选择优先级, 用逗号分割 例: "hevc,av1,avc"
  -q, --dfn-priority <dfn-priority>              画质优先级,用逗号分隔 例: "8K 超高清, 1080P 高码率, HDR 真彩, 杜比视界"
  -info, --only-show-info                        仅解析而不进行下载
  --show-all                                     展示所有分P标题
  -aria2, --use-aria2c                           调用aria2c进行下载(你需要自行准备好二进制可执行文件)
  -ia, --interactive                             交互式选择清晰度
  -hs, --hide-streams                            不要显示所有可用音视频流
  -mt, --multi-thread                            使用多线程下载(默认开启)
  --video-only                                   仅下载视频
  --audio-only                                   仅下载音频
  --danmaku-only                                 仅下载弹幕
  --sub-only                                     仅下载字幕
  --cover-only                                   仅下载封面
  --debug                                        输出调试日志
  --skip-mux                                     跳过混流步骤
  --skip-subtitle                                跳过字幕下载
  --skip-cover                                   跳过封面下载
  --force-http                                   下载音视频时强制使用HTTP协议替换HTTPS(默认开启)
  -dd, --download-danmaku                        下载弹幕
  --skip-ai                                      跳过AI字幕下载(默认开启)
  --video-ascending                              视频升序(最小体积优先)
  --audio-ascending                              音频升序(最小体积优先)
  --allow-pcdn                                   不替换PCDN域名, 仅在正常情况与--upos-host均无法下载时使用
  -F, --file-pattern <file-pattern>              使用内置变量自定义单P存储文件名:

                                                 <videoTitle>: 视频主标题
                                                 <pageNumber>: 视频分P序号
                                                 <pageNumberWithZero>: 视频分P序号(前缀补零)
                                                 <pageTitle>: 视频分P标题
                                                 <bvid>: 视频BV号
                                                 <aid>: 视频aid
                                                 <cid>: 视频cid
                                                 <dfn>: 视频清晰度
                                                 <res>: 视频分辨率
                                                 <fps>: 视频帧率
                                                 <videoCodecs>: 视频编码
                                                 <videoBandwidth>: 视频码率
                                                 <audioCodecs>: 音频编码
                                                 <audioBandwidth>: 音频码率
                                                 <ownerName>: 上传者名称
                                                 <ownerMid>: 上传者mid
                                                 <publishDate>: 收藏夹/番剧/合集发布时间
                                                 <videoDate>: 视频发布时间(分p视频发布时间与<publishDate>相同)
                                                 <apiType>: API类型(TV/APP/INTL/WEB)

                                                 默认为: <videoTitle>
  -M, --multi-file-pattern <multi-file-pattern>  使用内置变量自定义多P存储文件名:

                                                 默认为: <videoTitle>/[P<pageNumberWithZero>]<pageTitle>
  -p, --select-page <select-page>                选择指定分p或分p范围: (-p 8 或 -p 1,2 或 -p 3-5 或 -p ALL 或 -p LAST 或 -p 3,5,LATEST)
  --language <language>                          设置混流的音频语言(代码), 如chi, jpn等
  -ua, --user-agent <user-agent>                 指定user-agent, 否则使用随机user-agent
  -c, --cookie <cookie>                          设置字符串cookie用以下载网页接口的会员内容
  -token, --access-token <access-token>          设置access_token用以下载TV/APP接口的会员内容
  --aria2c-args <aria2c-args>                    调用aria2c的附加参数(默认参数包含"-x16 -s16 -j16 -k 5M", 使用时注意字符串转义)
  --work-dir <work-dir>                          设置程序的工作目录
  --ffmpeg-path <ffmpeg-path>                    设置ffmpeg的路径
  --mp4box-path <mp4box-path>                    设置mp4box的路径
  --aria2c-path <aria2c-path>                    设置aria2c的路径
  --upos-host <upos-host>                        自定义upos服务器
  --force-replace-host                           强制替换下载服务器host(默认开启)
  --save-archives-to-file                        将下载过的视频记录到本地文件中, 用于后续跳过下载同个视频
  --delay-per-page <delay-per-page>              设置下载合集分P之间的下载间隔时间(单位: 秒, 默认无间隔)
  --host <host>                                  指定BiliPlus host(使用BiliPlus需要access_token, 不需要cookie, 解析服务器能够获取你账号的大部分权限!)
  --ep-host <ep-host>                            指定BiliPlus EP host(用于代理api.bilibili.com/pgc/view/web/season, 大部分解析服务器不支持代理该接口)
  --tv-host <tv-host>                            自定义tv端接口请求Host(用于代理api.snm0516.aisee.tv)
  --area <area>                                  (hk|tw|th) 使用BiliPlus时必选, 指定BiliPlus area
  --config-file <config-file>                    读取指定的BBDown本地配置文件(默认为: BBDown.config)
  --version                                      Show version information
  -?, -h, --help                                 Show help and usage information


Commands:
  login    通过APP扫描二维码以登录您的WEB账号
  logintv  通过APP扫描二维码以登录您的TV账号
  serve    以服务器模式运行
```