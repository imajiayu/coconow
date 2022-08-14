<template>
	<el-tabs
		v-model="editableTabsPath"
		type="card"
		class="demo-tabs"
		closable
		@tab-change="changeActive"
		@tab-remove="removeTab"
	>
		<el-tab-pane
			v-for="item in editableTabs"
			:key="item.path"
			:label="item.label"
			:name="item.path"
		>
			<!--div :key="item.path" v-for="item in editableTabs"-->
			<ace-editor height="100%"
				:key="item.path"
				:pid="props.pid"
				:uid="props.uid"
				:path="item.path"
        		:mode="item.mode"
				:member-msg="props.memberMsg"
			/>
		</el-tab-pane>
	</el-tabs>
</template>
<script  setup>
import { onMounted, ref,onUnmounted } from "vue";
import eventBus from "@/assets/js/EventBus";
import AceEditor from "@/components/AceEditor.vue";
import { ElMessage,ElMessageBox } from 'element-plus'
import { ElLoading } from 'element-plus'
import {useRouter} from 'vue-router'
const router = useRouter()
const props = defineProps({
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
})
const modeTable = {
  "cpp":"c_cpp",
  "c":"c_cpp",
  "h":"c_cpp",
  "html":"html",
  "js":"javascript",
  "css":"css",
  "scss":"scss",
  "json":"json",
  "java":"java",
  "py":"python",
  "md":"markdown",
  "txt":"text",
  "text":"text",
  "in":"text",
  "out":"text",
  "v":"verilog",
  "makefile":"makefile",
  "Makefile":"makefile",
  "sh":"sh"
}
const editableTabsPath = ref('')
const editableTabs = ref([])
let saveWait = null
let operationSocket = null


const openfile = (e) => {addTab(e.label, e.path)}
const sendOperation = (e) => {
	console.log('eventBus receive',e,operationSocket)
	operationSocket.send(e.msg_json)
}
const saveAllFiles = () => {
    operationSocket.send(JSON.stringify({type:"saveAll",pid:props.pid}))
	saveWait = ElLoading.service({fullscreen:true,text:"on saving..."})
}


onMounted(() => {
	// console.log('tabs prop', props.pid, props.uid)
	eventBus.on('openfile',openfile )
	eventBus.on('sendOperation', sendOperation)
  eventBus.on("saveAllFiles",saveAllFiles)
	operationSocket = new WebSocket('ws://' + props.host + 'editor/')
	operationSocket.onmessage = function (e) {
		let delta = JSON.parse(e.data)
		//console.log("tabs recv",delta)
		if(delta.type == "saveDone")
		{
			saveWait.close()
			ElMessage.success({message:"保存成功!",showClose:true})
		}
		else if(delta.type == "refresh")
		{
			eventBus.emit("refresh",delta)
		}
		else if(delta.type=="openFail"){
			ElMessage.error({message:delta.message,showClose:true})
		}
		else if(delta.type == 'memberDisconnect' || delta.type == 'memberConnect')
		{
			// console.log('OnlineMemberChange',delta)
			eventBus.emit('OnlineMemberChange',delta)
		}
		else if(delta.type == 'deleteMember')
		{
			console.log("deleteMember",delta)
			if(props.uid == delta.uid)
			{
				ElMessage.error({message:"您已经被移出项目",showClose:true})
				router.push({name:'UserSpace'})
			}
		}
		else if(delta.type == "initializeTabs")
		{
			// console.log('OnlineMemberChange',delta)
			eventBus.emit("OnlineMemberChange",{uid:props.uid,pid:props.pid,group:delta.group})
			eventBus.emit('receiveOperation', { delta })
		}
		else 
			eventBus.emit('receiveOperation', { delta })
	}
	operationSocket.onopen = function (e) {
		// console.log('Operation socket opened')
		let msg = {}
		msg['type'] = 'initializeTabs'
		msg['uid'] = props.uid
		msg['pid'] = props.pid
		let msg_json = JSON.stringify(msg)
		operationSocket.send(msg_json)
	}
	operationSocket.onclose = function (e) {
		ElMessage.error("连接断开...")
		if(saveWait!=null)
			saveWait.close();
		// console.error('Operation socket closed unexpectedly')
	}
})
onUnmounted(() => {
	operationSocket.close()


		// console.log('tabs prop', props.pid, props.uid)
	eventBus.off('openfile', openfile)
	eventBus.off('sendOperation', sendOperation)
  eventBus.off("saveAllFiles",saveAllFiles)
})
const changeActive = (name) => {
	eventBus.emit('focus', { path: name })
}
const addTab = (label, path) => {
  for (const tab of editableTabs.value) {
    if (tab.path == path) {
      editableTabsPath.value = path;
      return;
    }
  }
  // 检查用户打开的文件后缀，如果不存在后缀或者非法后缀，则不打开
  let index = path.lastIndexOf(".");
  let appends = path.substr(index + 1)
  if(index == -1)//则直接截取文件名
  {
    appends = label
  }
  if (!(appends in modeTable))
  {
    ElMessage.warning({message:"无法识别文件类型",showClose:true})
    return 
  }
  
  editableTabs.value.push({
    path: path,
    label: label,
    mode:modeTable[appends],
  });
  editableTabsPath.value = path;
};
const removeTab = (path) => {
	// console.log('remvoe tab', path)
	const tabs = editableTabs.value
	let activePath = editableTabsPath.value
	if (activePath === path) {
		tabs.forEach((tab, index) => {
			if (tab.path === path) {
				const nextTab = tabs[index + 1] || tabs[index - 1]
				if (nextTab) {
					activePath = nextTab.path
				} else activePath = ''
			}
		})
	}
	editableTabsPath.value = activePath
	editableTabs.value = tabs.filter((tab) => tab.path !== path)

	//向后端通知关闭页面
	

}
</script>
<style scoped>
.demo-tabs {
	height: 100%;
}
.demo-tabs > .el-tabs__content {
	padding: 0px;
	color: #6b778c;
	font-size: 32px;
	font-weight: 600;
	height: 100%;
}
.el-tab-pane {
	padding: 0px;
	color: #6b778c;
	font-size: 32px;
	font-weight: 600;
	height: 100%;
}
</style>