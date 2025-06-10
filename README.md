## 目录结构
解压后生成以下两个子目录

* demo-service，包含各中间件的使用示例代码，代码在src/main/java目录下的com.alibaba.example包中。
* demo-start，包含启动类`com.alibaba.example.Application`。中间件使用示例的单元测试代码在`src/test/java`目录下的`com.alibaba.example`包中。日志配置文件为`src/main/resources`目录下的logback-spring.xml。
* 使用springmvc的代码在`src/main/java`目录下的`com.alibaba.example`包中。

## 使用方式
### 在开发工具中执行
将工程导入eclipse或者idea后，直接执行包含main方法的类`com.alibaba.example.Application`。

### 使用fat jar的方式
这也是pandora boot应用发布的方式。首先执行下列命令打包

```sh
mvn package
```

如果选择了auto-config，可在命令后加

```sh
-Dautoconfig.userProperties={fullPath}/bootstrap-start/antx.properties
```

通过-D参数指定antx.properties的位置，否则会进入autoconfig的交互模式

然后进入`demo-start/target`目录，执行fat jar

```sh
java -Dpandora.location=${sar} -jar demo-start-1.0.0.jar
```

其中${sar}为sar包的路径

### 使用 SarLauncher

这也是pandora boot应用发布到服务器上启动的方式。首先执行下列命令打包

```sh
mvn clean package -DskipTests
```

如果选择了auto-config，可在命令后加

```sh
-Dautoconfig.userProperties=demo-start/antx.properties
```

通过-D参数指定antx.properties的位置，否则会进入autoconfig的交互模式

打包之后，会有一个 unzip 日志，比如：

```
main:
[unzip] Expanding: /private/tmp/demo/demo-start/target/demo-start-1.0.0.jar into /private/tmp/demo/demo-start/target/ai-learning-demo
```

进入到unzip的目录，启动SarLauncher：

```
cd demo-start/target/ai-learning-demo/

java -Dpandora.location=${sar} com.taobao.pandora.boot.loader.SarLauncher
```

其中${sar}为sar包的路径

### 通过mvn命令直接启动
第一次调用前先要执行

```sh
mvn install
```

如果maven工程的Artifact，group id，version等都未变化，只需执行一次即可。

然后直接通过命令执行start子工程

```sh
mvn -pl demo-start pandora-boot:run
```

以上两个命令，如果选择了auto-config，可在命令后加

```sh
-Dautoconfig.userProperties={fullPath}/demo-start/antx.properties
```

通过-D参数指定antx.properties的位置，否则会进入autoconfig的交互模式properties的位置

## 升级指南

* https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/changelog

## Docker 模板

* APP-META 目录里
* https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/docker

## aone发布
请参考文档 https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/aone-guide

## 用户提示
* 启动工程报错：`-Djps.track.ap.dependencies=false`,可以参考：https://gitlab.alibaba-inc.com/middleware-container/bootstrap/issues/118812
* jdk17应用本地IDEA启动要添加相应的JVM参数，例如：
```
--add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/sun.net.util=ALL-UNNAMED
```
* jdk17应用中间件的单元测试要添加相应的JVM参数，例如工程根目录pom文件中的maven-surefire-plugin插件添加了JVM参数

## 相关链接
### Pandora Boot
* 钉钉交流群 ： 11701173
* wiki ： https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/home
* FAQ: https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/faq

### AppInsights（应用诊断利器，面向单机诊断的一站式解决方案，帮助应用诊断各种疑难杂症，让一线研发对自己负责的应用真正做到了如指掌。）
* 线上 ： https://start.alibaba-inc.com
* 日常 ： https://start.taobao.net
* 文档 ： https://aliyuque.antfin.com/shqigg/zfw52o

### Logger配置

* logger配置: https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/log-config

### Docker相关链接
* 如果工程有docker模板，目录是 APP-META，docker模板的说明文件是：APP-META/README.md
* docker参考说明：https://gitlab.alibaba-inc.com/middleware-container/pandora-boot/wikis/docker
* Aone-Standard-Runtime提供标准的aone运行时环境，用户只需关心yaml配置，无需手动维护Dockerfile和运维脚本，请见[ASR介绍](https://aliyuque.antfin.com/asr/user-manual/welcome)

### 构建工具:maven3
* https://aliyuque.antfin.com/build2art/yx6wcx/izfbf9bg5erg9fhy

### maven插件
error-prone(默认全局启用),jacoco-maven-plugin(默认全局启用),maven-surefire-plugin
* https://yuque.antfin.com/jh374881/ynknvt/oe6t7m
* https://yuque.antfin.com/jh374881/ynknvt/ycd83p

### JVM参数
* https://yuque.antfin.com/aone355606/migration/from-8-to-11#neuYz














