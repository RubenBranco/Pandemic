"use strict";

function fillDistrict(data, _district=false, county=false) {
    for (var i = 0; i < data.length; i++) {
        var district = data[i];
        $("#id_district").append("<option value='" + district['name'] + "'>" + district['name'] + "</option>");
    }
    if ($("#id_county").has('option').length === 0) {
        $("#id_district").trigger("change");
    }
    if (_district !== false) {
        var options = [];
        $("#id_district option").each(function(){
            options.push($(this).val());
        });
        var indice = options.indexOf(_district) + 1;
        $.ajax({type:'GET', url:'/api/districts/' + indice}).done(function(data){fillCounty(data, [_district, county])});
    }
}

function fillCounty(data, set=false) {
    for (var i = 0; i < data.length; i++) {
        var county = data[i];
        $("#id_county").append("<option value='" + county['name'] + "'>" + county['name'] + "</option>");
    }
    if (set !== false) {
        $("#id_district option[value='" + set[0] + "']").prop("selected", 'selected');
        $("#id_county option[value='" + set[1] + "']").prop("selected", "selected");
    }
}
function main() {
    $("#id_country").select2();
    $("#id_district").select2();
    $("#id_county").select2();
    $("#id_country").change(function() {
        if ($(this).val() === "PT"){
            $.ajax({type:'GET', url:'/api/districts/'}).done(function(data){fillDistrict(data)});
        } else {
            if ($("#id_district").length > 0) {
                $("#id_district").empty();
                $("#id_county").empty();
            }
        } 
    });
    $("#id_district").change(function() {
        $("#id_county").empty();
        var options = [];
        $("#id_district option").each(function(){
            options.push($(this).val());
        });
        var indice = options.indexOf($(this).val()) + 1;
        $.ajax({type:'GET', url:'/api/districts/' + indice}).done(function(data){fillCounty(data)});
    });
    if ($("#id_country").val() === "PT" && $("#id_district").has('option').length === 0) {
        $("#id_country").trigger("change");
    }
}

$(document).ready(function(){main()})