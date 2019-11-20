const apiSearchPlace = "/api/v1.0/places/";

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

