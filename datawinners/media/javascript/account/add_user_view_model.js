var viewModel = function () {
    var self = this;
    this.fullName = DW.ko.createValidatableObservable({value: ""});
    this.email = DW.ko.createValidatableObservable({value: ""});
    this.title = DW.ko.createValidatableObservable({value: ""});
    this.mobilePhone = DW.ko.createValidatableObservable({value: ""});
    this.questionnaires = ko.observableArray([]);
    this.selectedQuestionnaires = ko.observableArray([]);
    this.role = DW.ko.createValidatableObservable({value: ""});
    this.hasFetchedQuestionnaires = ko.observable(false);
    this.addUserSuccess = ko.observable(false);
    this.hasFormChanged = ko.observable(false);

    this.fullName.subscribe(function () {
        DW.ko.mandatoryValidator(self.fullName, 'This field is required');
        self.hasFormChanged(true);
    });

    this.email.subscribe(function () {
        var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
        DW.ko.regexValidator(self.email, 'Invalid email id', re);
        self.hasFormChanged(true);
    });

    this.mobilePhone.subscribe(function () {
        var re = /^([0-9]{5,15})$/i;
        DW.ko.regexValidator(self.mobilePhone, 'Invalid phone number', re);
        self.hasFormChanged(true);
    });

    this.role.subscribe(function () {
        self.hasFormChanged(true);
        self.role.setError(null);
    });

    this.submit = function () {
        $.blockUI({
            message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
            css: {width: '275px'}
        });

        var formData = {
            'title': self.title(),
            'full_name': self.fullName(),
            'username': self.email(),
            'role': self.role(),
            'mobile_phone': self.mobilePhone(),
            'selected_questionnaires': self.selectedQuestionnaires() || [],
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        };
        $.post('/account/user/new/', formData, function (response) {
            var responseJson = $.parseJSON(JSON.stringify(response));
            if (responseJson['add_user_success'] == true) {
                self.addUserSuccess(true);
                self.clearFields();
                $('html, body').animate({scrollTop: '0px'}, 0);
            } else {
                var errors = responseJson['errors'];
                self.parseErrors(errors);
            }
        });
    };

    this.parseErrors = function (errors) {
        if (errors['username']) {
            self.email.setError(errors['username'][0]);
        }
        if (errors['mobile_phone']) {
            self.mobilePhone.setError(errors['mobile_phone'][0]);
        }
        if (errors['full_name']) {
            self.fullName.setError(errors['full_name'][0]);
        }
        if (errors['role']) {
            self.role.setError(errors['role'][0]);
        }
    };

    this.fetchQuestionnaires = function () {
        if (self.role() == 'Project Managers') {
            $.getJSON('/entity/questionnairesandpolls/', {}, function (data) {
                $('#container_content').height('auto');
                self.hasFetchedQuestionnaires(true);
                self.questionnaires(data['questionnaires']);
            });
        }
        return true;
    };

    this.clearFields = function () {
        this.fullName(null);
        this.email(null);
        this.email.setError(null);
        this.title(null);
        this.role(null);
        this.mobilePhone(null);
        this.mobilePhone.setError(null);
        this.fullName.setError(null);
        this.questionnaires([]);
        this.hasFetchedQuestionnaires(false);
        this.selectedQuestionnaires([]);
        this.hasFormChanged(false);
        setTimeout(function () {
            self.addUserSuccess(false);
        }, 4000)
    }
};

$(document).ready(function () {
    var userModel = new viewModel();
    window.userModel = userModel;
     if ($('#option_administrator')[0] === undefined) {
        userModel.role('Project Managers');
        userModel.fetchQuestionnaires();
    }
    userModel.hasFormChanged(false);
    ko.applyBindings(userModel, $("#user_profile_content")[0]);

    $('a[href]:visible').bind('click', function (event) {
        if(userModel.hasFormChanged()) {
            window.redirectUrl = $(this).attr('href');
            $("#form_changed_warning_dialog").dialog("open");
            return false;
        }
        return true;
    });

    var kwargs = {
        container: "#form_changed_warning_dialog",
        continue_handler: function () {
            window.location.href = window.redirectUrl;
        },
        title: gettext("Your change(s) will be lost"),
        cancel_handler: function () {
        },
        height: 150,
        width: 550
    };

    DW.delete_user_warning_dialog = new DW.warning_dialog(kwargs);

});
