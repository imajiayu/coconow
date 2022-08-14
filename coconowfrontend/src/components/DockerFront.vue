<template>
    <div style="width:100%;height:100%;" id="terminal"></div>
</template>

<script>
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit';
  export default {
    props:{
      pid:{
        type:Number,
        required:true,
        default:9
      },
      uid:{
        type:Number,
        required:true,
        default:9
      },
      host:{
        type:String,
        required:true,
        default:"124.70.221.116:8000/"
      }
      
    },
    name: 'webssh',
    data () {
      return {
        term: null,
        terminalSocket: null,
        order:'',
      }
    },
    methods: {
    },
    beforeUpdate(){
      // console.log("before update")
      resizeScreen()
    },
    mounted () {
      //实例化一个websocket，用于和django交互
      this.terminalSocket = new WebSocket("ws://"+this.host+"web/");
        //获取到后端传回的信息
      this.terminalSocket.onopen = () => {
        this.terminalSocket.send(JSON.stringify({type:'init',uid:this.uid,pid:this.pid}))
      }
      this.terminalSocket.onmessage = (res) => {
        // console.log("onmessge:",res.data);
        // var message = JSON.parse(res.data);
        //将传回来的数据显示在xterm里
        this.term.write(res.data);
        //重置要发送的信息
        this.order = ""
      } 
      //ws连接的时候
      // this.terminalSocket.onopen = function(){
      //     console.log('websocket is Connected...')
      // }
      //ws关闭的时候
      // this.terminalSocket.onclose = function(){
      //     console.log('websocket is Closed...')
      // }
      //ws错误的时候
      // this.terminalSocket.onerror = function(){
      //     console.log('damn Websocket is broken!')
      // }
      // this.term.attach(this.terminalSocket)
      // 绑定xterm到ws流中 },
      let terminalContainer = document.getElementById('terminal')
      //创建xterm实例
      this.term = new Terminal({
        rendererType: 'canvas', // 渲染类型
        rows: 10, // 行数
        convertEol: true, // 启用时，光标将设置为下一行的开头
        scrollback: 10, // 终端中的回滚量
        disableStdin: false, // 是否应禁用输入。
        cursorStyle: 'bar', // 光标样式
        cursorBlink: true, // 光标闪烁
        theme: {
          foreground: 'black', // 字体
          background: 'white', // 背景色
          cursor: 'black' // 设置光标
        }
      })                     // 创建一个新的Terminal对象



      const fitAddon = new FitAddon()
      this.term.loadAddon(fitAddon)
      fitAddon.fit()
      window.addEventListener("resize", resizeScreen)
      function resizeScreen() {
        try { // 窗口大小改变时，触发xterm的resize方法使自适应
          fitAddon.fit()
        } catch (e) {
          console.log("e", e)
        }
      }

      this.term.open(terminalContainer)              // 将term挂载到dom节点上

      //this.term.writeln("Welcome to \x1b[1;32m墨天轮\x1b[0m.")
      //this.term.writeln('This is Web Terminal of Modb; Good Good Study, Day Day Up.')
      
      this.term.prompt = _ => {
        this.term.write("\r\n$ ")
      }
      //在xterm上显示命令行提示
      //this.term.prompt()
      //监听xterm的键盘事件
      
      this.term.onData(async key => {
        
        //let pattern = new RegExp("[\u4E00-\u9FA5]+");
        //if(pattern.test(key))
        //  return;
        
        console.log('term on data: \"',key,'\"')
        this.terminalSocket.send(JSON.stringify({type:'opt',opt:key}))
        return 
        //enter键
        if (key.charCodeAt(0) === 13) {
          // 将行数据进行添加进去
          if (currentLineData !== '') {
          //将当前行数据传入历史命令数组中存储
            historyLineData.push(currentLineData)
              //定义当前行命令在整个数组中的位置
            last = historyLineData.length - 1
          }
          //当输入clear时清空终端内容
          if (currentLineData === 'clear') {
            term.clear()
          }

        //在这可以进行发起请求将整行数据传入

          // 清空当前行数据
          currentLineData = ''

          term.write(`\r\n${terminalTitleTemplate}: `)
        } else if (key.charCodeAt(0) === 127) {
          //删除键--》当前行偏移量x大于终端提示符所占位置时进行删除
          if (term._core.buffer.x > terminalTitleTemplate.length + 1) {
            currentLineData = currentLineData.slice(0, -1)
            term.write('\b \b')
          }
        } else if (key === '\u001b[A') {
          //up键的时候
          let len = 0
          if (historyLineData.length > 0) {
            len = historyLineData.length + 1
          }

          if (last < len && last > 0) {
              //当前行有数据的时候进行删除掉在进行渲染上存储的历史数据
            for (let i = 0; i < currentLineData.length; i++) {
              if (term._core.buffer.x > terminalTitleTemplate.length + 1) {
                term.write('\b \b')
              }
            }
            let text = historyLineData[last - 1]
            term.write(text)
              //重点，一定要记住存储当前行命令保证下次up或down时不会光标错乱覆盖终端提示符
            currentLineData = text

            last--
          }
        } else if (key === '\u001b[B') {
          //down键
          let lent = 0
          if (historyLineData.length > 0) {
            lent = historyLineData.length - 1
          }
          if (last < lent && last > -1) {
            for (let i = 0; i < currentLineData.length; i++) {
              if (term._core.buffer.x > terminalTitleTemplate.length + 1) {
                term.write('\b \b')
              }
            }
            let text = historyLineData[last + 1]
            term.write(text)
            currentLineData = text
            last++
          }
        } else {
          
          
          //啥也不做的时候就直接输入
          //currentLineData += key
          term.write(key)
        }
      })
      /*
      this.term.onKey((ev)=>{ 
        //这里我改了一下，就是收到一个字符就发一个字符，要不然显示效果上不太好。
        //目前来说，前端就是转发用户的所有按键，相当于用户直接操纵SSH
        // key是输入的字符 ev是键盘按键事件
        console.log("send:",ev.key,ev.keyCode);
        this.terminalSocket.send(JSON.stringify({type:'opt',opt:ev.key}))
        return 
        const printable = !ev.domEvent.altKey && !ev.domEvent.altGraphKey && !ev.domEvent.ctrlKey && !ev.domEvent.metaKey
        console.log("key==========", ev);
        
        if (ev.domEvent.keyCode == 13) { // 输入回车
        
          this.term.write('\b'.repeat(this.order.length))

          this.order+='\n'
          this.terminalSocket.send(this.order)

          this.order=''
          console.log("里面的order",this.order)
        }
        else if(ev.domEvent.keyCode == 8){//删除按钮
          //截取字符串[0,lenth-1]
          if(this.order=='')
            return;
          this.order = this.order.substr(0,this.order.length-1)
          //清空当前一条的命令
          this.term.write("\b \b")
          //简化当前的新的命令显示上
          //this.term.write("$ "+this.order)
          console.log("截取的字符串"+this.order)
          typeof this.order
        }
        else if(printable){// 将每次输入的字符拼凑起来
          this.order += ev.key
          this.term.write(ev.key)
          console.log("外面的order",this.order)}
        })
        */
        /*
        this.term.onData(key => {  // 粘贴的情况
          if(key.length > 1) this.term.write(key)
        })*/

        resizeScreen()
    },
    unmounted() {
      this.terminalSocket.close()
    },
     
  }
</script>
<style scoped>
@import 'xterm/css/xterm.css'
</style>