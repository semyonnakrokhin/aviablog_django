$(document).ready(function() {
    var fieldIndex = 1; // Индекс для генерации уникальных имен полей

    // Обработчик клика на кнопку "Добавить поле"
    $('.add-field-btn').click(function() {
        var field = '<div class="form-group row mb-3 align-items-center field">' +
                        '<div class="col">' +
                            '<div class="input-group p-2">' +
                                '<input type="file" name="track_image_' + fieldIndex + '" class="form-control-file track-image-field">' +
                                '<button type="button" class="btn btn-danger btn-sm remove-field-btn">' +
                                    '<i class="fas fa-minus-circle"></i>' +
                                '</button>' +
                            '</div>' +
                        '</div>' +
                    '</div>';
        $('#fields-container').append(field);
        fieldIndex++; // Увеличение индекса для следующего поля

        updateFormAttributes(); // Вызов функции updateFormAttributes
    });

    // Обработчик клика на кнопку "Удалить поле"
    $(document).on('click', '.remove-field-btn', function() {
        $(this).closest('.field').remove();
        updateFormAttributes(); // Вызов функции updateFormAttributes
    });

    // Функция для обновления атрибутов формы
    function updateFormAttributes() {
        var trackImageFields = $('.track-image-field');
        trackImageFields.each(function(index) {
            var fieldName = 'track_image_' + index;
            $(this).attr('name', fieldName); // Обновление имени поля
        });
    }
});

