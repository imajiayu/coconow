<template>
  <el-container class="homeroot">
    <el-header style="height:8%;border-bottom: solid rgba(219, 219, 219, 0.874);">
      <Header
        :avatar="`/static/avatar/${uid}.jpg?${Date.now()}`"
        >当前正在编辑：
        <el-avatar 
          v-for="item in OnlineMsgList"
          :key="item.id"
          :style="'border:3px solid '+item.color"
          :size="40" 
          :src="item.headSrc + `?${Date.now()}`" />
      </Header>
    </el-header>
    <el-container style="height:92%;">
      <el-aside>
        <file-tree 
          :pid="pid"
          :uid="uid" />
        <!--Menu /-->
      </el-aside>
      <el-container height="100%" class="editor-area">
        <el-main height="100%">
          <div class="box" id="editorbox">
            <tabs 
              class="left" 
              id="editorlid" 
              :pid="pid" 
              :uid="uid" 
              :host="host"
              :member-msg="memberMsgList"
              />
            <resize
              :leftstart="230"
              lid="editorlid"
              rid="editorrid"
              rbox="editorbox"
            />
            <chat 
              class="right" 
              id="editorrid"
              :pid="pid"
              :uid="uid"
              :host="host"
              :member-msg="memberMsgList"
               />
          </div>
        </el-main>
        <el-footer>
          <docker-front 
          :uid="uid" 
          :pid="pid"
          :host="host" />
        </el-footer>
      </el-container>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted, ref,computed ,onUnmounted} from "vue";
import Header from "../components/Header.vue";
import AceEditor from "@/components/AceEditor.vue";
import FileTree from "@/components/FileTree.vue";
import Tabs from "@/components/Tabs.vue";
import DockerFront from "@/components/DockerFront.vue";
import Chat from "@/components/Chat.vue";
import { ElMessage,ElMessageBox } from 'element-plus'
import Resize from "@/components/Resize.vue";
import eventBus from "@/assets/js/EventBus";
import axios from 'axios'
import Cookies from 'js-cookie'
import { useRouter } from "vue-router";
const router = useRouter();

const pid = Number(router.currentRoute.value.query.pid);
const uid = Number(Cookies.get("uid"));
const host = "124.70.221.116:8000/"

// console.log("home props", typeof pid, pid, typeof uid, uid);
const memberMsgList = ref([])
const OnlineUid = ref([])
let OnlineMsgList = computed(() => {
  return memberMsgList.value.filter(item => OnlineUid.value.indexOf(item.id) != -1)
})

const OnlineMemberChange = (data) => {
  // console.log("OnlineMemberChange",data)
  let ruid = data.uid 
  let usrname = ""
  for(const item of memberMsgList.value)
  {
    if(item.id == ruid)
    {
      usrname = item.username
      break
    }
  }
  if(data.type == "memberDisconnect"){
    if(usrname != "" && ruid != uid)
      ElMessage.success("您的队友" + usrname + "已离线")
    else if(ruid != uid)
      ElMessage.warning("未知队友离线")
  }
  else {
    if(usrname != "" && ruid != uid)
      ElMessage.success("您的队友" + usrname + "已上线")
    else if(ruid != uid)
      ElMessage.warning("未知队友上线")

  }
  OnlineUid.value = data.group
}

onUnmounted(()=> {
  eventBus.off('OnlineMemberChange', OnlineMemberChange)  
})
onMounted(() => {
  axios.get(`/api/projects/info/${pid}/`)
  .then((response) => {
    let msglist = response.data.membermsg
    for(let i = 0;i<msglist.length;++i)
    {
      let msg = msglist[i];
      msg['headSrc'] = `/static/avatar/${msg.id}.jpg`
    }
    memberMsgList.value = msglist
    // console.log("project",memberMsgList.value)
  })
  .catch(function (error) {
    console.log('error',error.response);
    if(error.response && error.response.status == 403)
        ElMessage.warning(error.response.data);
    else
        ElMessage.warning('未知错误')
  });
  eventBus.on('OnlineMemberChange', OnlineMemberChange)  
})

</script>

<style lang="scss" scoped>

.homeroot{
    position:fixed;
    padding:0;
    margin:0;

    top:0;
    left:0;

    width: 100%;
    height: 100%;
}
.el-aside {
  border-right: solid rgba(219, 219, 219, 0.874);
  width: 230px;
  height: 100%;
  background-color: rgb(255, 255, 255);
}
.el-footer {
  border-top: solid rgba(219, 219, 219, 0.874);
  height: 25%;
  width: 100%;
  padding-top: 0;
  padding-bottom: 0%;
  padding-left: 13px;
  padding-right: 0px;
  background-color: rgb(255, 255, 255);
}
.el-main {
  height: 80%;
  padding: 0;
}
.editor-area {
  height: 100%;
}

.box {
  display: block;
  overflow: visible;
  white-space: nowrap;
  width: 100%;
  height: 100%;
}

.left {
  display: inline-block;
  vertical-align: top;
  width: 70%;
  height: 100%;
  /*float:left;*/
  background-color: white;
}

.right {
  display: inline-block;
  vertical-align: top;
  /*float:left;*/
  width: 29%;
  height: 100%;
  background-color: white;
}
</style>
