$(document).ready(function(){
    $("#all").click(function(){
        $.getJSON("/souall",{
            w:"all"
        },function(data){
            clearInterval(t1)
            console.log(data)
            var html_con = ''
            data[1].forEach(function(value,i){
                html_con += '<ul class="list-group">'
                value.forEach(function(val,n){
                    if(n==0){
                        html_con += '<li class="list-group-item header">'+val+'</li>'
                    }else{
                        html_con += '<li class="list-group-item">'+val+'</li>'
                    }
                })
                html_con += '</ul>'
            })
            $("#show").html(html_con)

            html_sts += '<ul class="list-group">'
            data[0].forEach(function(value,i){
                        html_sts += '<li class="list-group-item header">'+value+'</li>'
            })
            html_sts += '</ul>'
            $("#sts").html(html_sts)
        })
        var num = 0
        var t1 = self.setInterval(function(){
            if(num<100){
                num_con = '<div class="num_con alert alert-info">稍等一会儿'+ new Array(num).join("》") + '</div>'
            }else{
                num_con = '<div class="num_con alert alert-info">别等了，查不出来了</div>'
                clearInterval(t1)
            }

            $("#show").html(num_con)
            num++
        },1000)
    })
})