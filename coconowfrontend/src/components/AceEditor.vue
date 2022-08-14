
<template>
	<div
		class="ace-editor"
		ref="acediv"
	></div>
</template>

<script>
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/snippets/javascript'
import 'ace-builds/src-noconflict/snippets/html'
import 'ace-builds/src-noconflict/snippets/css'
import 'ace-builds/src-noconflict/snippets/scss'
import 'ace-builds/src-noconflict/snippets/json'
import 'ace-builds/src-noconflict/snippets/java'
import 'ace-builds/src-noconflict/snippets/python'
import 'ace-builds/src-noconflict/snippets/markdown'
import 'ace-builds/src-noconflict/snippets/text'
import 'ace-builds/src-noconflict/snippets/c_cpp'
import 'ace-builds/src-noconflict/snippets/verilog'
import 'ace-builds/src-noconflict/snippets/makefile'
import 'ace-builds/src-noconflict/snippets/sh'


import 'ace-builds/webpack-resolver'
import 'ace-builds/src-noconflict/ext-language_tools'
import 'ace-builds/src-noconflict/theme-monokai'
import 'ace-builds/src-noconflict/mode-javascript'
import 'ace-builds/src-noconflict/theme-clouds'
import { Queue } from '@/assets/js/Queue'
import { ref, toRefs, reactive, onMounted,onUnmounted, onBeforeUnmount } from 'vue'
import {
	Operation,
	Client,
	isRetain,
	isDelete,
	isInsert,
	transform,
	OperationFromJSON,
} from '@/assets/js/OperationTransformation'
import eventBus from '@/assets/js/EventBus'

export default {
	props: {
		mode: {
			type: String,
			required: false,
			default: 'c_cpp',
		},
		theme: {
			type: String,
			required: false,
			default: 'clouds',
		},
		content: {
			type: String,
			required: false,
			default: '',
		},
		pid: {
			type: Number,
			required: true,
			default: 31,
		},
		path: {
			type: String,
			required: true,
			default: '/home/temp.py',
		},
		uid: {
			type: Number,
			required: true,
			default: 9,
		},
        memberMsg:{
            type:Object,
            require:true,
        }
	},
	setup(props) {
		var silent = false
		var Range = ace.require('ace/range').Range
		var aceEditor = null
		var mark_queue = new Queue()
		var client = null
		var doc = null
		var docEndLength = 0
		var mytime = new Date().getTime()
		const acediv = ref(null)
		const data = reactive({
			markcolor: 'rgba(0,255,0,0.4)',
			curcolor:'rgba(0,255,0,0.4',
		})
		const focus = (e) => {
			// console.log('focus:', e.path)
			if (e.path == props.path) {
				aceEditor.focus()
			}
		}
		const initializeFromServer = function (delta) {
      		console.log("initialize delta",delta)
			client.revision = delta['revision']
			let s = doc.indexToPosition(0)
			
			aceEditor.setReadOnly(false)

			aceEditor.session.insert(s, delta['content'])
			docEndLength += delta['content'].length

		}

		const receiveOperation = (e) => {
			let delta = e.delta
			if(delta.path != props.path){
				return;
			}
			// console.log('revice', delta, mytime)
			silent = true
			if (delta['type'] == 'initializeFile') {
				initializeFromServer(delta)
			} else if (delta['type'] == 'ack') {
				client.serverAck()
			} else if (delta['type'] == 'nak') {
				client.resend()
			} else if (delta['type'] == 'operation') {
				// console.log("markcolor",delta)
				for(const msg of props.memberMsg)
					if(msg.id == delta.uid)
					{
						// console.log("markcolor",msg,data.markcolor)
						data.markcolor=msg.color
						break
					}
				// console.log(client.state,delta['operation'])
				client.applyServer(OperationFromJSON(delta['operation']))
			}
			silent = false
		}
		onUnmounted(()=>{
			
			console.log("read only onunmounted",aceEditor.getReadOnly())
			if(aceEditor.getReadOnly()==false){
				let msg = {}
				msg['type'] = 'closeFile'
				msg['uid'] = props.uid
				msg['pid'] = props.pid
				msg['path'] = props.path
				let msg_json = JSON.stringify(msg)
				eventBus.emit('sendOperation', { msg_json })
			}

			eventBus.off("receiveOperation",receiveOperation)
			eventBus.off("focus",focus)
		})
		onMounted(() => {
			//首先建立连接
			// console.log('ace props', props.pid, props.uid)
			eventBus.on('focus', focus)
			eventBus.on('receiveOperation', receiveOperation)
			client = new Client()
			client.sendOperation = function (revision, operation) {
				let msg = {}
				msg['type'] = 'operation'
				msg['uid'] = props.uid
				msg['pid'] = props.pid
				msg['path'] = props.path
				msg['revision'] = revision
				msg['operation'] = operation

				let msg_json = JSON.stringify(msg)
				eventBus.emit('sendOperation', { msg_json })
				// console.log(msg_json)
			}
			client.applyOperation = function (operation) {
				// console.log("apply",docEndLength,operation)
				var ops = operation.ops
				var index = 0
				for (var i = 0, l = ops.length; i < l; i++) {
					var op = ops[i]
					if (isRetain(op)) {
						index += op
					} else if (isInsert(op)) {
						applyInsert(index, op)
						index += op.length
					} else if (isDelete(op)) {
						applyDelete(index, -op)
					}
				}
			}

			const applyInsert = function (index, str) {
				let start = doc.indexToPosition(index)
				let end = aceEditor.session.insert(start, str)

				let id = addmark(
					start.row,
					start.column,
					end.row,
					end.column,
					'marker'+data.markcolor.substr(1)
				)
				// console.log("markercolor",data.markcolor)
				// console.log(id)
				mark_queue.enqueue(id)
				window.setTimeout(removemark, 1000)
				docEndLength += str.length
			}

			const applyDelete = function (index, num) {
				if (num < 0) {
					num = -num
				}
				let s = doc.indexToPosition(index)
				let t = doc.indexToPosition(index + num)
				let remove_range = { start: s, end: t }
				aceEditor.session.remove(remove_range)
				docEndLength -= num
			}

			const initialize = function () {
				let msg = {}
				msg['type'] = 'initializeFile'
				msg['uid'] = props.uid
				msg['pid'] = props.pid
				msg['path'] = props.path
				let msg_json = JSON.stringify(msg)
				eventBus.emit('sendOperation', { msg_json })
			}

			initialize()

		
			aceEditor = ace.edit(acediv.value, {
				fontSize: 18,
				value: props.content,
				theme: 'ace/theme/' + props.theme,
				mode: 'ace/mode/' + props.mode,
				wrap: true,
				tabSize: 4,
			})
			aceEditor.setReadOnly(true)
			console.log("read only",aceEditor.getReadOnly())
			doc = aceEditor.session.getDocument()

			aceEditor.setOptions({
				enableSnippets: true,
				enableLiveAutocompletion: true,
				enableBasicAutocompletion: true,
			})
			aceEditor.session.on('change', function (delta) {
				// console.log('aceedtor', mytime, ',', silent)
				if (silent) return

				// console.log('change:', delta)
				if (delta.action == 'remove') {
					var fromIndex = doc.positionToIndex(delta.start)
					var delete_num = delta.lines.join('\n').length
					var restLength = docEndLength - fromIndex - delete_num
					var operation = new Operation()
						.retain(fromIndex)
						.delete(delete_num)
						.retain(restLength)
					docEndLength -= delete_num
				} else if (delta.action == 'insert') {
					var fromIndex = doc.positionToIndex(delta.start)
					var insert_str = delta.lines.join('\n')
					var restLength = docEndLength - fromIndex
					var operation = new Operation()
						.retain(fromIndex)
						.insert(insert_str)
						.retain(restLength)
					docEndLength += insert_str.length
				}
				// console.log(operation)
				client.applyClient(operation)
			})
			//aceEditor.session.addMarker(new Range(1, 0, 1, 5), 'marker', "text");
		})

		const addmark = (srow, scol, erow, ecol, color) => {
			let range = new Range(srow, scol, erow, ecol)
			range.start = aceEditor.session.doc.createAnchor(range.start)
			range.end = aceEditor.session.doc.createAnchor(range.end)
			var id = aceEditor.session.addMarker(range, color)
			return id
		}

		const removemark = () => {
			let id = mark_queue.dequeue()
			aceEditor.session.removeMarker(id)
		}
		return {
			acediv,
			...toRefs(data),
		}
	},
}
</script>
 
<style lang='scss'>
.ace-editor {
	min-height: 600px;
}
.marker {
	position: absolute;
	background-color: v-bind(markcolor);
}

.markerFF0000 {
	position: absolute;
	background-color: #FF000066;
}

.markerFFFF00 {
	position: absolute;
	background-color: #FFFF0066;
}

.marker008000 {
	position: absolute;
	background-color: #00800066;
}

.marker0000FF {
	position: absolute;
	background-color: #0000FF66;
}

.markerFFA500 {
	position: absolute;
	background-color: #FFA50066;
}

.marker008B8B {
	position: absolute;
	background-color: #008B8B66;
}

.marker8A2BE2 {
	position: absolute;
	background-color: #8A2BE266;
}

.markerFFC0CB {
	position: absolute;
	background-color: #FFC0CB66;
}



.blue {
	position: absolute;
	//attachment: local;
	background-color: blue;
}
.ace-container {
	position: relative;

	.config-panel {
		position: absolute;
		right: 0;
		bottom: 0;
		width: 50%;
		height: 100%;
		overflow: scroll;
		box-shadow: grey -5px 2px 3px;
		background-color: rgba(255, 255, 255, 0.5);
		z-index: 1;

		.item {
			margin: 10px auto;
			text-align: center;

			.title {
				color: white;
				margin: 0 10px;
				font-size: 14px;
			}
		}
	}

	.bookmarklet {
		position: absolute;
		right: 0;
		bottom: 0;
		width: 20px;
		height: 20px;
		z-index: 2;
		cursor: pointer;
		border-width: 9px;
		border-style: solid;
		border-color: lightblue gray gray rgb(206, 173, 230);
		border-image: initial;
	}
}
</style>
