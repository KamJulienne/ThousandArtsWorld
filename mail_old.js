// ┌──────────────────────────────────────┐
// │ 千艺界 邮箱配置 · 抗逆向混淆层       │
// │ 密钥分片异或 + 多轮编码保护          │
// └──────────────────────────────────────┘
(function(){
var _x=atob("hQUBNTqSW8VL+IXU2N+I4A==");
var _f=[[218,94,92,112,13,190,96,242],[4,170,177,235,225,231,142,237],[176,94,85,66,202,32,230,191],[29,62,108,247,22,188,135,2],[50,82,117,33,126,33,19,210],[239,10,248,60,95,240,25,128]];
var _k=[];
for(var _i=0;_i<_f.length;_i++){
 for(var _j=0;_j<_f[_i].length;_j++){
  _k.push(_f[_i][_j]^((_i*13+_j*7+42)%256));
 }
}
var _p='';
for(var _i=0;_i<_x.length;_i++){
 var _c=_x.charCodeAt(_i)^_k[_i%_k.length];
 if(_c===0)break;
 _p+=String.fromCharCode(_c);
}
window.EC={
 host:'smtp.qq.com',
 port:587,
 username:'bisir@foxmail.com',
 password:_p,
 to:'bisir@foxmail.com',
 from_name:'千艺界性格测试'
};
})();