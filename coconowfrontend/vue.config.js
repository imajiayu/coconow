const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  publicPath:'./',
  outputDir:'dist',
  assetsDir:'static',
  devServer: {
      client: {
        webSocketURL: 'ws://0.0.0.0:8080/ws',
      },
      proxy: {
        '/api': {	
          target: 'http://124.70.221.116:8000/',//'http://172.105.118.225:4523/mock/866496/', //接口域名
          changeOrigin: true,             //是否跨域
          ws: false,
        },
        '/static': {	
          target: 'http://124.70.221.116:8000/',//'http://172.105.118.225:4523/mock/866496/', //接口域名
          changeOrigin: true,             //是否跨域
          ws: false,
        },
      }
  }
};