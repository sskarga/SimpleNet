const apiSearchPlace = "/api/v1.0/places/";

/*
let checkCity = localStorage.getItem('cities');

if (checkCity) {
    dataCity = JSON.parse(localStorage.getItem("cities"));
} else {
    $.getJSON(apiSearchPlace + "сities")
        .done(function (json) {
            dataCity = json.results;
            localStorage.setItem("cities", JSON.stringify(json.results));
        })
        .fail(function (jqxhr, textStatus, error) {
            var err = textStatus + ', ' + error;
            console.log("Request Failed: " + err);
        });
}
;
*/
jQuery(document).ready(function ($) {

            $('#сities').select2({
                language: "ru",
                theme: "bootstrap",
                placeholder: "Выберите город",
                allowClear: true,
                ajax: {
                    url: apiSearchPlace + "сities",
                    dataType: 'json',
                    quietMillis: 250,
                    cache: true,
                },
            });
    /*
    $('#сities').select2({
        language: "ru",
        theme: "bootstrap",
        placeholder: "Выберите город",
        allowClear: true,
        data: dataCity,
    });
*/

    $('#street').select2({
        language: "ru",
        theme: "bootstrap",
        placeholder: "Выберите улицу/район",
        allowClear: true,
        minimumInputLength: 2,
        ajax: {
            url: apiSearchPlace + "streets",
            dataType: 'json',
            quietMillis: 250,
            cache: true,
            data: function (params) {
                return {
                    q: params.term,
                    id: $('#сities').val(),
                };
            },
        },
    });


    $('#building').select2({
        language: "ru",
        theme: "bootstrap",
        placeholder: "Выберите дом",
        allowClear: true,
        minimumInputLength: 1,
        ajax: {
            url: apiSearchPlace + "buildings",
            dataType: 'json',
            quietMillis: 250,
            cache: true,
            data: function (params) {
                return {
                    q: params.term,
                    id: $('#street').val(),
                };
            },
        },
    });

    $('#сities').change(function () {
        $(".search-building").addClass(" disabled");
    });

    $('#street').change(function () {
        $(".search-building").addClass(" disabled");
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
})
;

