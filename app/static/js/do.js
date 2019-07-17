$(document).ready(function(){
    $("#all").click(function(){
        $.getJSON("/souall",{
            w:"all"
        },function(data){
            clearInterval(t1)
            console.log(data)
        })
        var num = 0
        var t1 = self.setInterval(function(){
            $("#show").html(num+"")
            num++
        },1000)
    })
})