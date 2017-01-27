$(document).ready(function () {

    var infoFormButton = $('#downloader-info-button');
    var infoAlert = $('#downloader-info-alert');
    var infoForm = $('#downloader-info-form');
    var infoFormButtonCancel = $('#downloader-info-cancel');
    var exportButtons = $('.export-button');


    if (Cookies.get('downloader')) {
        infoAlert.hide();
        exportButtons.removeClass('disabled');
    }

    infoFormButton.click(function () {
        infoForm.slideDown();
    });

    infoFormButtonCancel.click(function () {
        infoForm.slideUp();
        infoForm[0].reset()
    });

    infoForm.submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: "post",
            url: "/transnet/create_download_user",
            data: {
                "name": $('#downloader-name-input').val(),
                "organization": $('#downloader-organization-input').val(),
                "purpose": $('#downloader-purpose-input').val(),
                "email": $('#downloader-email-input').val(),
                "url": $('#downloader-url-input').val(),
                "csrf_token": $('#csrf_token').val()
            },
            success: function (data) {
                if (data && data['uuid'] !== 'Nan') {
                    Cookies.set('downloader', data['uuid'], {expires: 100});
                    infoAlert.hide();
                    exportButtons.removeClass('disabled');
                    infoForm.slideUp();
                }
            }
        });

    });

});
