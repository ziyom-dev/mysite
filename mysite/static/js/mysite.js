$(document).ready(function() {
    // Функция для обновления ссылки
    function updateLink() {
        var site_url = "https://itpapa.uz/";
        var shop_url = "shop/";
        var category_url = "category/";
        var sub_category_url = "subcategory/";
        // Извлекаем значение slug из input
        var slug = $('#id_slug').val();
        // Формируем полный URL
        var full_url = site_url + shop_url + category_url + sub_category_url + slug;
        // Обновляем href и текст для ссылки, если она уже есть, или создаем новую
        var $link = $('.your_class_here');
        if ($link.length) {
            $link.attr('href', full_url).text(full_url); // Обновляем и href, и текст
        } else {
            $('#header-title').after('<a href="' + full_url + '" class="your_class_here">' + full_url + '</a>');
        }
    }

    // Проверяем, соответствует ли текущий URL заданному шаблону
    if (window.location.pathname.match(/\/admin\/shop\/products\/edit\/\d+\//)) {
        console.log("Находимся на странице редактирования продукта");

        // Вызываем updateLink при загрузке страницы, чтобы инициализировать ссылку
        updateLink();

        // Добавляем обработчик события на изменение slug
        $('#id_slug').on('input change', updateLink);
    }
});
