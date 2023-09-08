---
layout:       post
title:      "模板"
subtitle:   "Open file with terminal Vim from the macOS Finder"
date:       2021-01-19 12:00:00
author:       "Hux"
catalog:      true
published:    false
header-style: text
tags:
    - Web
    - JavaScript
---

---
title: "「SF-PLF」1 Equiv"
subtitle: "Programming Language Foundations - Program Equivalence (程序的等价关系)"
layout: post
author: "Hux"
header-style: text
hidden: true
tags:
  - SF (软件基础)
  - PLF (编程语言基础)
  - Coq
  - 笔记
---


我的日常主力编辑器主要是：

- (Neo)Vim
- Spacemacs (via Emacs-plus)
- Visual Studio Code
- IntelliJ IDEA

![](/img/in-post/post-f-f-weibo.png)

How It works
------------

这里面只有 (Neo)Vim 是存活在终端中的（我并不在终端内使用 Emacs），而由于我日常主要是从终端（via iTerm）来使用电脑，所以会把他们都加入到 `$PATH` 里以方便从终端中唤起，VSCode 和 IDEA 都有一键加入的功能， Emacs 我在 `~/.zshrc` 中放了一个 `alias emacs='open -n -a Emacs.app .'` 解决。

但是，偶尔也会有从 Finder 中打开文件的需求，这时候如果通常会打开拓展名所绑定的 `Open with...` 应用，在大部分时候我的默认绑定是 VSCode，但是今天心血来潮觉得有没有办法直接打开 Vim 呢？搜了一下还真有基于 AppleScript 的解决方案：

1. 打开 `Automator.app`
2. 选择 `New Document`
3. 找到 `Run AppleScript` 的 action 双击添加
4. 编写 AppleScript 脚本来唤起终端与 vim （下文给出了我的脚本你可以直接稍作修改使用）
5. 保存为 `Applications/iTermVim.app` （你可以自己随便取）
6. 找到你想要以这种方式打开的文件，比如 `<随便>.markdown`，`⌘ i` 获取信息然后修改 `Open with` 为这个应用然后 `Change All...`

效果超爽 ;)

```applescript
on run {input, parameters}
  set filename to POSIX path of input
  set cmd to "clear; cd `dirname " & filename & "`;vim " & quote & filename & quote
  tell application "iTerm"
    activate
    tell the current window
      create tab with default profile
      tell the current session
        write text cmd
      end tell
    end tell
  end tell
end run
```

```coq
Instance showPair {A B : Type} `{Show A} `{Show B} : Show (A * B) :=
  {
    show p :=
      let (a,b) := p in 
        "(" ++ show a ++ "," ++ show b ++ ")"
  }.
Compute (show (true,42)).
```

我这里的代码是采取是用 `iTerm` 与唤起 `vim`、窗口置前、在新窗口中打开、同时 `cd` 到目录。你也可以改成用 macOS 自带的 `Terminal.app`、在新窗口而非新 tab 打开、应用不同的 profile、或是执行其他 executable 等……任你发挥啦。

### References

- [Open file in iTerm vim for MacOS Sierra](https://gist.github.com/charlietran/43639b0f4e0a01c7c20df8f1929b76f2)
- [Open file in Terminal Vim on OSX](https://bl.ocks.org/napcs/2d8376e941133ccfad63e33bf1b1b60c)


**补充两点：**

*   我支持「小程序」的产品价值，也支持 PWA 作为 Web 开放标准一部分的技术价值。
*   PWA 目前主要靠 Google 推动是客观事实，且 PWA 的发展必须依赖平台（浏览器）的参与。

**PWA（甚至整个 Web）似乎被 Google（Chrome）与「第三世界」绑到一起去了。**「这世界还有多少人没上过网、没有 4G、没有 3G……印度、印度尼西亚、非洲、乌干达……」这便是这两年的 Chrome Dev Summit 的主旋律了。