# coconow
Coconow是一个综合了代码编辑、代码编译、聊天室等多种功能且可多人实时共享代码的线上协作编程平台。项目前端地址：[https://gitlab.com/tj-cs-swe/cs10102302-2022/BigHard/coconow](https://gitlab.com/tj-cs-swe/cs10102302-2022/BigHard/coconow)，项目后端地址：[https://gitlab.com/tj-cs-swe/cs10102302-2022/BigHard/coconow_backend](https://gitlab.com/tj-cs-swe/cs10102302-2022/BigHard/coconow_backend)。

# 
# 项目简介

本项目是一个综合了代码实时协同编辑、代码编译、组内聊天的在线协作编程平台，解决了目前主流编程软件不易共享、共享平台不能进行代码编辑和编译的缺陷，提出了团队协作开发的新模式。本项目为使用者提供了如下功能：

* 账号管理：注册、登录、修改密码、更换头像
* 项目管理：创建项目、删除项目、邀请成员、删除成员
* 项目协作开发：添加文件、删除文件、上传文件、文件协同编辑、文件保存
* 代码编译运行
* 实时聊天
以上功能可以基本满足软件协作开发中的常见需求。

![image](https://user-images.githubusercontent.com/57378499/184522169-4323f122-914d-4ca6-ab03-a5831f823292.png)
![image](https://user-images.githubusercontent.com/57378499/184522178-a059cae8-124b-41a2-838a-e768631171bc.png)
![image](https://user-images.githubusercontent.com/57378499/184522198-cbb22abd-3d6e-4bfe-b501-0cd7ddc18cce.png)
![image](https://user-images.githubusercontent.com/57378499/184522204-a254a700-1438-45cc-9d57-5ff01f381006.png)
![image](https://user-images.githubusercontent.com/57378499/184522205-9d9e77ca-4f59-4201-803d-bfdf10519f34.png)
![image](https://user-images.githubusercontent.com/57378499/184522208-4a5ba6fa-afff-4565-9132-2ed9d7254eda.png)
![image](https://user-images.githubusercontent.com/57378499/184522210-25c636c9-8235-4056-ba6c-cc9009756447.png)
![image](https://user-images.githubusercontent.com/57378499/184522212-25f2313b-0bd0-4152-b9e6-e08887e193e8.png)


# 使用说明

## 功能说明

1. 账号管理
    * 进入首页后，点击注册可进行注册。需要使用tongji.edu邮箱接收验证码以完成注册。
    * 本网站只为已注册的用户提供服务。
    * 用户注册完成后可点击主页的登录按钮进行登录，用户名为该用户的唯一标识，且不能修改。
    * 用户名用户可个性化地修改自己的头像。
    * 登录之后，可点击标签栏相应按钮进行登出、修改信息等操作。
2. 项目管理
    * 所有用户均可在个人空间页面创建自己的项目。
    * 每个人可以创建多个项目，其拥有/参与的项目，将在其个人空间页面中以下拉列表形式呈现出来。在列表中可对项目进行管理。
    * 每个项目可以有多个成员，成员分“拥有者”与“普通成员”。“拥有者”即项目的创造者，可对项目成员进行增删；“普通成员”则是被邀请进项目的其他用户。“拥有者”与“普通成员”，对项目容器的操作权限是相同的，都可以增删文件、编辑文件。
    * 点击个人空间页某个项目下拉栏右上方的“删除项目”按钮，可以删除项目。
3. 共同编辑
    * 在个人空间页面点击某个项目，将跳转进入该项目的编辑页面。
    * 该页面左侧是文件目录树，提供“新建文件”、“新建文件夹”、“上传文件”、“刷新目录树”、“保存”等多个按钮。亦可在目录树上点击鼠标右键进行各种文件操作。
    * 页面主体部分是编辑器窗口。支持多个项目成员共同编辑，类似各大共享文档的效果。
    * 为了区分各个成员的编辑记录，系统将为每个成员分配一个专属颜色，相关信息在页面上方显示，成员每次对文件进行修改操作后，修改部位的文字会短暂地以该成员的专属颜色高亮显示。
    * 编辑器支持 ctrl+z （撤销）、ctrl+c（复制）、ctrl+v（粘贴）等常用快捷键操作。
    * 文本编辑的内容，系统会自动保存，一般不需要手动保存。
4. 虚拟环境控制台
    * 在项目编辑页面的底部，是一个命令行窗口，可以通过它来控制该项目的容器。
    * 大体可以当作一个 ssh 连接，可进行 touch、mkdir、gcc 等命令。
5. 实时聊天
    * 在项目编辑页面的右侧，是聊天窗口，是当前项目的一个独立聊天室，可供项目内成员交谈。
    * 进入编辑页面后会自动同步历史消息。
    * 聊天窗口有记录列表和“发送消息”“查询历史消息”两个输入框。输入框内键入相应信息后按回车提交。
    * 查询历史消息，将筛选出包含所键入字符串的历史消息。若键入字符串为空，将显示所有历史消息。
    * 连天窗口与编辑器窗口之间有个纵向拖动条，可拖动以调整宽度。
# 其他说明

1. 在本系统各个页面的头部（注册页面除外），均有导航栏，提供“登录”、“登出”、“设置”、“进入我的空间”等操作。
# 安装部署

## 依赖安装&运行

### **1.前端**

* 前端项目基于vue.js和element-plus库开发而成。在解压之后，可直接在目录下使用命令 `npm install` 安装全部依赖项。
* 为了使得前后端能够正常通讯，需要指定前端转发对接的端口，在项目根目录下的  `vue.config.js` 文件中修改端口。默认后端端口8000，如需要修改，将'/api'和'/static'两个proxy中的端口修改为需要的端口，并将websocket中的url中的端口修改即可。
* 完成上述配置后，可使用命令  `npm run serve` 一件启动前端环境。默认端口8080，如果已被占用将顺次后延。
### **2.后端**

部署系统：Ubuntu 20.04 server 64bit

### 依赖

Docker 20.10.14

```plain
docker源不断更新，参考官网安装步骤
https://docs.docker.com/engine/install/ubuntu/
```
MySQL  Ver 8.0.28-0ubuntu0.20.04.3 for Linux on x86_64 ((Ubuntu))
```plain
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql.service
```
Redis 5.0.7
```plain
apt install redis
```
python依赖包已经放在requirements.txt中
```plain
pip install -r requirements.txt
```
### 修改coconow/settings.py

ALLOWED_HOSTS为允许访问的主机IP

```plain
ALLOWED_HOSTS = ['124.70.221.116','127.0.0.1']
```
修改数据库设置
当前数据库中需要有一个名为 ’coconow’的空数据库，所登录mysql用户需要拥有对其所有的权限

```plain
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'coconow',
        'HOST': '127.0.0.1',
        'PROT': 3306,
        'USER': 'bighard',
        'PASSWORD':'BigHard1_'
    }
}
```
邮箱设置，给用户发送验证码时用到的邮箱
```plain
EMAIL_FROM='41001189@qq.com'
EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp.qq.com' # 腾讯QQ邮箱 SMTP 服务器地址 
EMAIL_PORT = 25 # SMTP服务的端口号 
EMAIL_HOST_USER = '41001189@qq.com' #你的qq邮箱，邮件发送者的邮箱 
EMAIL_HOST_PASSWORD = 'gpsnbtvziyrbbjeg' #你申请的授权码（略） 
EMAIL_USE_TLS = False #与SMTP服务器通信时,是否启用安全模式
```
### 启动

在根目录下输入以下命令以启动后端

```plain
python manage.py makemigrations
python manage.py migrate
python manage.py runserver <ip>:<port>
```

# 开发与维护

## 注意事项与说明

* 本项目前端采用了vue3+element-plus的开发方法，并不能直接兼容element-ui，请注意版本上的差异。
## 项目目录结构

* 前端
└── coconow //根目录

    ├── babel.config.js

    ├── interface.md 

    ├── jsconfig.json

    ├── **node_modules**

    ├── package.json      		 //包信息

    ├── package-lock.json

    ├── README.md          		 //readme

    ├──**src**            		 //开发路径

	│	├── App.vue

	│	├── **assets**				 //部分前端资源，图片等

	│	├──**components**		 //组件，供其它位置调用

	│	│   ├── 404.vue			 //404页面

	│	│   ├── AceEditor.vue    //文编编辑器页面

	│	│   ├── Chat.vue		 //聊天室

	│	│   ├── DockerFront.vue  //Docker前端展示

	│	│   ├── FileTree.vue	 //文件树

	│	│   ├── ForgetPassword.vue  //忘记密码，可重置密码

	│	│   ├── Header.vue		 //顶行栏

	│	│   ├── Login.vue		 //登陆界面

	│	│   ├── Register.vue     //注册见面

	│	│   ├── Resize.vue       //修改聊天室大小

	│	│   ├── Revise.vue       //上传头像、修改密码

	│	│   └── Tabs.vue		 //文件编辑器打开列表

	│	├── main.js

	│	├── package.json		

	│	├── **router**				 //路由

	│	│   └── index.js		 //设置路由和各个页面

	│	└── **views**				 //视图

	│	    ├── Home.vue         //编辑界面主题

	│	    └── UserSpace.vue    //项目管理界面

	└── vue.config.js			 //项目参数，可修改转发目的地

* 后端
coconow/

├── **accounts**

│   ├── admin.py

│   ├── apps.py

│   ├── **init**.py

│   ├── models.py //模型定义

│   ├── tests.py

│   ├── **urls**

│   │   ├── account.py //用户信息路由

│   │   ├── init.py

│   │   ├── project.py //项目管理路由

│   ├── **views**

│   │   ├── account.py //用户信息业务逻辑

│   │   ├── init.py

│   │   ├── project.py //项目管理业务逻辑

│   └── walkTree.py

├── **coconow**

│   ├── asgi.py

│   ├── init.py

│   ├── routing.py 

│   ├── settings.py //全局设置

│   ├── urls.py //全局路由

│   └── wsgi.py

├── **file**

│   ├── admin.py

│   ├── apps.py

│   ├── init.py

│   ├── models.py

│   ├── tests.py

│   ├── tools.py //工具函数

│   ├── urls.py //文件系统路由

│   └── views.py //文件系统业务逻辑

├── manage.py

├── static

│   └── avatar //用户头像

│       └── default.jpg  

├── tempeditfile //协作编辑时的临时文件

├── tempfile //上传下载时的临时文件

└── **websocket_service**

    ├── admin.py

    ├── apps.py

    ├── ChatRoom.py //聊天室

    ├── CoProgramming.py //协作编程

    ├── init.py

    ├── models.py

    ├── tests.py

    ├── urls.py

    ├── views.py

    └── WebSSH.py //webSSH功能

Django后端总共分为4大应用，分别为：

1. **coconow** 模块全局设置与路由设置
2. **accounts** 用户信息与项目管理
3. **file** 项目文件管理
4. **websocket_service** 3个使用websocket的模块，分别为：
    * webssh
    * 协作编程
    * 聊天室
## 维护者

该项目由同济大学计算机科学与技术专业BigHard团队开发维护。

如有其他问题或建议，欢迎通过邮件联系2480902326@qq.com。
