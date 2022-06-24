function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function event() {
    return {
    type : "net.contargo.logistics.tams.TBD",
    site : "terminal",
    timestamp : new Date().toISOString(),
    version : "v1",
    producer : "ccs.automodal.contargo.net",
    location : "DEKOB",
    guid : uuidv4(),
    }
}

container = []
stacks = []

function get_container(){
    $.getJSON("http://localhost/container", function ( data) {
        if (JSON.stringify(data) !== JSON.stringify(container)) {
            container = data
            console.log("container", container)
            select = $("#FormUnitSelect")
            crane = $("#crane-details-container")
            select.empty()
            for (id in container) {
                if (container[id].stack === "crane") {
                    crane.text("Container: " + container[id].number)
                } else {
                    crane.text("Container: none")
                }
                select.append($("<option></option>").attr("value", id).text(container[id].number + " [" + container[id].stack + "]"))
            }
            update_stack_table()
        }
    })}

function get_stacks() {
    $.getJSON("http://localhost/stacks", function (data) {
        if (JSON.stringify(data) !== JSON.stringify(stacks)) {
            stacks = data
            console.log("stacks", stacks)
            select = $("#FormTargetSelect")
            select.empty()
            for (id in stacks) {
                space = stacks[id].height - stacks[id].container.length
                select.append($("<option></option>").attr("value", id).text(stacks[id].name + " [" + stacks[id].container.length + "]" + " [" + space + "]"))
            }
        }
        update_stack_table()
    })
}

function get_details(){
    $.getJSON("http://localhost/details", function ( data) {
        console.log("details", data)
        if (data["feature"].length !== 0) {
            feature_list = $( "#feature-list" )
            feature_list.empty()
            for (id in data["feature"]) {
                type = data["feature"][id].type
                version = data["feature"][id].version
                feature_list.append($("<li></li>").text(type + " " + version))
            }
        }
    })
}

function get_messages(){
    $.getJSON("http://localhost/messages", function ( data) {
        if (data["msg"].length !== 0) {
            for (msg in data["msg"]) {
                color = "<span>"
                if (data["msg"][msg].type !== "OK") { 
                    color = '<span class="text-danger">'
                }
                $("#messages-console").prepend(
                    color + '$> <b>' + data["msg"][msg].title +':</b> ' +data["msg"][msg].text +'</span><br>'
                );
               
            }
        }
        //
    })  
}

function get_job(){
    $.getJSON("http://localhost/job", function ( data) {
        jobcard = $( "#running-job" )
        console.log("JOB:", data)
        jobcard.empty()
        if ($.isEmptyObject(data)){
            jobcard.append("no running job")
        }else{
            jobcard.append("<ul>" +
                "<li><b>type:</b> " + data.type + "</li>" + 
                "<li><b>x:</b> " + data.target.x + "</li>" + 
                "<li><b>y:</b> " + data.target.y + "</li>" + 
                "<li><b>z:</b> " + data.target.z + "</li>" + 
                "<li><b>unit nr:</b> " + data.unit.number + "</li>" + 
                "<li><b>unit id:</b> " + data.unit.unit_id + "</li>" + 
                "<li><b>unit type:</b> " + data.unit.type + "</li>" + 
                "</ul>")
        }
    })
}

function update_stack_table(){
    stacks_table = $( "#stacks table tbody" )
    stacks_table.empty()
    crane_container = ""
    for (id in container){
        if (container[id].stack === "crane"){
            crane_container = container[id].number
        }
    }
    
    stacks_table.append("<tr></tr>")
    last = stacks_table.children("tr:last")
    for (id in stacks) {
        last.append("<td>" + stacks[id].name + "</td>")
    }
    last.append("<td>crane</td>")
    
    indexes = [2,1,0]
    for (idx in indexes){
        stacks_table.append("<tr></tr>")
        
        last = stacks_table.children("tr:last")
        for (ids in stacks) {
            if (stacks[ids].container.length > indexes[idx]){
                last.append("<td>" + stacks[ids].container[indexes[idx]].number + "</td>")
            }
            else{
                last.append("<td>-</td>")
            }
        }
        if (indexes[idx] === 0){
            if (crane_container === ""){
                last.append("<td>-</td>")
            }else {
                last.append("<td class='bg-danger'>" + crane_container + "</td>")
            }
        }else{
            last.append("<td>-</td>")
        }
    }
}
    
$(document).ready(function () {
    $.getJSON("http://localhost/state", function ( data) {
        console.log("state", data)
    })
    
    get_details()
    get_container()
    get_stacks()
    
    setInterval(function(){ 
        get_messages()
    }, 500);
    
    setInterval(function(){ 
        get_job()
        get_container()
        get_stacks()
    }, 1000);
    
    $( "#send-job" ).click(function (){
        unitform = $("#FormUnitSelect option:selected")
        targetform = $("#FormTargetSelect option:selected")
        unit = container[ unitform.val()]
        target = stacks[targetform.val()]
        if (unit.number !== unitform.text()) {
            console.log("SEND JOB FAILED unit.number !== unitform.text()")
            console.log(unit.number, unitform.text())
        }
        data = {
            "metadata": event(),
            "type": $("#FormTypeSelect option:selected").val(),
            "target": target.coordinates, // Coordinaten
            "unit": unit, // CCSUNIT
        }
        console.log("job", data)
        $.ajax({ url: "job", 
            data: JSON.stringify(data),
            type:"POST",
            contentType:"application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                console.log(data)
            }
        })
    })
});
