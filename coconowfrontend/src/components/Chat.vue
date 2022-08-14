<template>
    <el-container style="height:100%;user-select: none;">
        <!--el-card style="width:100%; margin: 0px 0px 0px"-->

        <el-main style="height:75%">
            <el-scrollbar ref="scrollMessage" style="height:100%" >
                <div class="already" v-for="item in messages" :key="item">
                    <div class="tips" v-if="item.isdivider">
                        {{ item.msg }}
                    </div>
                    <div class="message" v-else-if="item.self && item.show" style="flex-direction:row-reverse">
                        <el-avatar
                            :size="40" 
                            :style="'border:3px solid '+item.color"
                            v-bind:src="item.avatar"
                        />
                        <p @dblclick="copyMSG(item.msg)">{{ item.msg }} </p>
                    </div>
                    <div class="message" v-else-if="item.show">
                        <el-avatar
                            :size="40" 
                            :style="'border:3px solid '+item.color"
                            v-bind:src="item.avatar"
                        />
                        <p @dblclick="copyMSG(item.msg)"> {{ item.msg }}</p>
                    </div>
                </div>
            </el-scrollbar>
        </el-main>

        <el-footer style="height:25%">
            <el-input
                v-model="inputSearch"
                placeholder="筛选历史消息，键入空则显示所有消息"
                maxlength=100
                @keyup.enter.native="submit_search"
            />
            <br/>
            <el-input
                v-model="textarea"
                :rows="3"
                type="textarea"
                placeholder="发送消息"
                resize="none"
                autofocus=true
                maxlength=200
                show-word-limit
                @keyup.enter.native="submit_msg"
            />
            <!--el-button @click="submit_msg">Add</el-button-->
        </el-footer>

        <!--/el-card-->
    </el-container>
</template>


<script>
import { ref } from 'vue';

import { ElMessage } from 'element-plus'

const textarea = ref('');
const inputSearch = ref('');
let chat_socket;
let avatars = [
    "https://gsp0.baidu.com/5aAHeD3nKhI2p27j8IqW0jdnxx1xbK/tb/editor/images/client/image_emoticon3.png",
    "https://gsp0.baidu.com/5aAHeD3nKhI2p27j8IqW0jdnxx1xbK/tb/editor/images/client/image_emoticon6.png",
    "https://gsp0.baidu.com/5aAHeD3nKhI2p27j8IqW0jdnxx1xbK/tb/editor/images/client/image_emoticon15.png",
    "https://gsp0.baidu.com/5aAHeD3nKhI2p27j8IqW0jdnxx1xbK/tb/editor/images/client/image_emoticon95.png",
];


export default ({
    data() {
        return {
            textarea: textarea,
            inputSearch: inputSearch,
            messages: [],
        }
    },
    props:{
        pid: {
            type: Number,
            required: true,
            default: 31,
        },
        uid: {
            type: Number,
            required: true,
            default: 9,
        },
        host: {
            type: String,
            required: false,
            default: '124.70.221.116:8000/',
        },
        memberMsg:{
            type:Object,
            require:true,
        }
    },
    mounted() {
//===============================================================================
        if (typeof (WebSocket) == "undefined") {
            console.log('your browser doesn\'t support WebSocket.');
        } else {
            // console.log('your browser supports WebSocket.');
            //let socketUrl = "ws://10.80.42.223:2014/";
            let socketUrl = "ws://"+this.host+"chat/";
            if (chat_socket != null) {
                chat_socket.close();
                chat_socket = null;
            }

            // 开启一�???? websocket 服务
            chat_socket = new WebSocket(socketUrl);
            // console.log(chat_socket);
            //打开事件
            chat_socket.onopen = this.socket_connected;
            //浏览器端接收消息
            chat_socket.onmessage = this.recv_msg;
            //关闭事件
            chat_socket.onclose = function() {
                // console.log('websocket closed');
                //document.getElementById('id-button-connected').innerHTML="offline";
            }
            //发生了错误事�????
            chat_socket.onerror = function() {
                console.log('websocket error');
                //document.getElementById('id-button-connected').innerHTML="error";
            }
        }
//===============================================================================
    },
    
    unmounted() {
      chat_socket.close()
    },
    watch:{
        memberMsg:function(newMsg,oldMsg){
            // console.log("memberMsg:",oldMsg,newMsg,this.memberMsg)
            // console.log("memberMsg:",this.messages,this.messages.length)
            for(var i = 0 ;i<this.messages.length;++i)
            {
                let msg  = this.messages[i]
                // console.log("memberMsg:",msg)
                if(msg.uid != null){
                    msg.avatar = this.getAvatars(msg.uid)
                    msg.color = this.getColor(msg.uid)
                    // console.log("memberMsg:",msg)
                }
            }
        }
    },
    methods: {
        getColor(uid){
            for(const msg of this.memberMsg)
            {
                if(msg.id == uid)
                {
                    return msg.color
                }
            }
            return ""
        },
        getAvatars(uid) {
            // console.log("avatars",uid,this.memberMsg)
            for(const msg of this.memberMsg)
            {
                if(msg.id == uid)
                {
                    return msg.headSrc + `?${Date.now()}`
                }
            }
            return "https://gsp0.baidu.com/5aAHeD3nKhI2p27j8IqW0jdnxx1xbK/tb/editor/images/client/image_emoticon3.png"
        },
        socket_connected() {
            // console.log('websocket opened.');
            //document.getElementById('id-button-connected').innerHTML="online";
            
            let msg = {};
            msg['type'] = 'initialize';
            msg['uid']=this.uid;
            msg['pid']=this.pid;
            let msg_json = JSON.stringify(msg);
            chat_socket.send(msg_json);
            // console.log("send", msg_json);
        },
        submit_msg() {
            // 发送chat事件
            textarea.value = textarea.value.replace(/\r|\n/ig,"");
            if (textarea.value.match(/^\s*$/)) {
                textarea.value="";
            }
            else {
                // console.log('submit');
                let msg = {};
                msg['type'] = 'message';
                msg['uid'] = this.uid;
                msg['message'] = textarea.value;
                msg['pid'] = this.pid;
                let msg_json = JSON.stringify(msg);
                chat_socket.send(msg_json);
                // console.log("send", msg_json);

                /*
                this.messages.push({
                    self: true,
                    avatar: this.getAvatars(this.uid),
                    msg: textarea.value,
                    show: true,
                    color:this.getColor(this.uid),
                })*/
                
                // 清空
                textarea.value="";
                this.$nextTick(function(){
                    this.$refs.scrollMessage.setScrollTop(1000000);
                });
            }
        },
        submit_search() {
            inputSearch.value = inputSearch.value.replace(/\r|\n/ig,"");
            if (inputSearch.value.match(/^\s*$/)) {
                for (var i=0; i<this.messages.length; i++) {
                    this.messages[i].show = true;
                }
                inputSearch.value="";
            }
            else {
                // console.log('search', inputSearch.value);
                //var patt = new RegExp(inputSearch.value);
                let patt = inputSearch.value;
                //console.log("patt", patt);
                for (let i=0; i<this.messages.length; i++) {
                    let flag = false;
                    let str = this.messages[i].msg;
                    //console.log("str", str);
                    //this.messages[i].show = patt.test(this.messages[i].msg);
                    if (str.length >= patt.length) {
                        for (let j=str.length-patt.length; !flag && j>=0; j--) {
                            for (let k=0; !flag && k<patt.length; k++) {
                                flag = true;
                                if (str[j+k] != patt[k]) {
                                    flag = false;
                                    break;
                                }
                            }
                            //console.log("??", j, flag);
                        }
                    }
                    this.messages[i].show = flag;
                    //console.log('msg', this.messages[i].msg, patt.test(this.messages[i].msg));
                }
                inputSearch.value="";
            }
            this.$nextTick(function(){
                this.$refs.scrollMessage.setScrollTop(1000000);
            });
        },
        recv_msg(msg) {
            // console.log('receive data', msg.data);
            var data = JSON.parse(msg.data);

            if (data['type'] == 'message') {
                this.messages.push({
                    self: this.uid==data['uid'],
                    uid:data['uid'],
                    avatar: this.getAvatars(data['uid']),
                    msg: data['message'],
                    show: true,
                    color:this.getColor(data['uid']),
                });
            }
            else if (data['type'] == 'initialize') {            
                var arr = data['records'];
                // console.log(arr);
                // console.log("initalize",this.memberMsg)

                for (var i=0; i<arr.length; i++) {
                    this.messages.push({
                        self: this.uid==arr[i]['uid'],
                        uid:arr[i]['uid'],
                        avatar: this.getAvatars(arr[i]['uid']),
                        msg: arr[i]['message'],
                        show: true,
                        color:this.getColor(arr[i]['uid']),
                    });
                }
                this.messages.push({
                    isdivider: 1,
                    msg: "history",
                    show: true,
                });
            }
            this.$nextTick(function(){
                this.$refs.scrollMessage.setScrollTop(1000000);
            });
        },
        copyMSG(msg) {
            //alert(msg);
            const input = document.createElement('input');
            input.setAttribute('readonly', 'readonly');
            input.value = msg;
            document.body.appendChild(input);
            //input.setSelectionRange(0, 999);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            ElMessage.success('复制成功'+msg);
        }
    }
})
</script>


<style scoped>

.already .message{
    width: 95%;
    display: flex;
    align-items:baseline;
    margin-left: 10px;
    flex-direction: row;
    margin: auto;
}

.already .message label{
    font-size: 14px;
    font-weight: 800;
    width: 50px;
    background-color: #fcc;
    border-radius: 3px;
}

.already .message p{
    font-size: 16px;
    margin-left: 5px;
    white-space: normal;
    margin-right: 5px;
    border: 1px solid rgba(141, 143, 141, 0.479);
    width: 50%;
    border-radius: 8px;
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 10px;
    padding-bottom:  10px;
    word-wrap: break-word;
}

.tips{
    width: "100%";
    font-size: 15px;
    text-align: center;
    background-color: rgba(231, 228, 228, 0.521);
    margin-top: 0;
    margin-bottom: 0;
}


</style>
