# 智慧树自动刷网课

## 介绍

自动化观看视频、回答视频中途弹出问题、完成章节测试。

---

## 说明

`db_course.py`:创建Course.db数据库与增删改查。

`db_answer.py`:创建Answer.db数据库与增删改查，以及导出Excel功能。

`crawl_answer.py`:爬取网页答案。

`auto.py`:selenium自动刷课。

`gui_auto.py`:功能集成GUI客户端。

`img`:存储登录滑块验证图片。

`Course.db`：存储用户各课程下的视频名称。

`Course.db`：存储各课程的章节答案。

`Lzy.ico`:GUI的LOGO。

`requirment.txt`:运行所需的python包。

`user_data.txt`:存储电话号码与登录密码。

`geckodriver.exe`:火狐浏览器驱动(Windows64)。

`geckodriver`:火狐浏览器驱动(Liunx64)。

---

## 运行环境

- `python>=3.10`

- 建议使用最新版火狐浏览器。自带火狐驱动（win64、liunx64），请根据自身系统选择适宜驱动。[火狐驱动地址](https://github.com/mozilla/geckodriver/releases)


- 安装所依赖python包：


	pip install -r requirement.txt

- 将`openpyxl/compat/numbers.py`中第41行`numpy.float`改为`float`
- Windows环境配置到此结束。

**Liunx：**

需格外做如下配置：

- 需要使用以下命令安装tkinter：

```
sudo apt install python3-tk
```

- 修改`auto.py`驱动代码：

```
windows:
s = Service("geckodriver.exe")
liunx:
s = Service("geckodriver")
```

- Liunx环境配置到此结束。

**启动**

`python gui_auto`启动客户端。

---

## 功能说明

`登录`：用户名、密码分为智慧树登录的手机号、密码。

![image-20231103111341236](/image-20231103111341236.png)

`答案来源网址`：可下拉选择答案来源的网址。

`清除数据`：销毁Answer.dn、Course.db数据库。

`课程名称`：`手动爬取`、刷课课程的目标。

`运行`：根据选项`是否观看网课`、`是否答题`开始刷课。

`返回`：返回登录界面。

`手动爬取`：爬取`课程名称`所对应的课程答案。

`导出答案`：将爬取的答案导出为xlsx格式。

`保存日志`：保存控制台输出日志。

![image-20231103111944373](/image-20231103111944373.png)
