const apiSearchPlace = "/api/v1.0/places/";

$('#city').select2({
    language: "ru",
    theme: "bootstrap",
});

$('#street').select2({
    language: "ru",
    theme: "bootstrap",
});

$('#building').select2({
    language: "ru",
    theme: "bootstrap",
});

$(document).ready(function() {
    $("#building").empty();
    $("#street").empty();

    $.ajax({
        type: "GET",
        url: apiSearchPlace + "сities",
        success: function (res) {
            if (res) {
                $("#city").append('<option value="0">Выберите город</option>');
                $.each(res, function () {
                    $.each(this, function (id, value) {
                        $("#city").append('<option value="' + id + '">' + value + '</option>');
                    });
                });
            }
        }
    });
});

$('#city').change(function () {
    let city_id = $(this).val();

    $("#building").empty();
    $("#street").empty();
    $(".search-building").addClass(" disabled");

    if ((city_id) && (city_id > 0)) {
        $.ajax({
                type: "GET",
                url: apiSearchPlace + "сities/" + city_id + "/streets",
                success: function (res) {
                    if (res) {
                        $("#street").append('<option value="0">Выберите улицу/район</option>');
                        $.each(res, function () {
                            $.each(this, function (id, value) {
                                $("#street").append('<option value="' + id + '">' + value + '</option>');
                            });
                        });
                    }
                }
            }
        )
    }
});

$('#street').change(function () {
    let street_id = $(this).val();

    $("#building").empty();
    $(".search-building").addClass(" disabled");

    if ((street_id) && (street_id > 0)) {
        $.ajax({
                type: "GET",
                url: apiSearchPlace + "streets/" + street_id + "/buildings",
                success: function (res) {
                    if (res) {
                        $("#building").append('<option value="0">Выберите сооружение</option>');
                        $.each(res, function () {
                            $.each(this, function (id, value) {
                                $("#building").append('<option value="' + id + '">' + value + '</option>');
                            });
                        });
                    }
                }
            }
        )

    };
});

$('#building').change(function () {
    let building_id = $(this).val();
    if ((building_id) && (building_id > 0)) {
        $(".search-building").removeClass("disabled");
        ;
    } else {
        $(".search-building").addClass(" disabled");
    }
    ;
});
