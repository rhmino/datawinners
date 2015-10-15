$(document).ready(function () {

    var analysisTable,
        colCustomization;

    var tableElement = $("#analysis_table");

    //Tooltip for long questionnaires on column customisation widget
    $('[data-toggle="tooltip"]').tooltip();

    var AnalysisPageDataTable = (function ($, tableElement) {
        function AnalysisPageDataTable(columns) {
            tableElement.DataTable({
                "pageLength": 25,
                "dom": '<ip<t>ipfl>',
                "language": {
                    "info": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s %(subject_type)s(s)"),
                        {
                            'start': '_START_',
                            'end': '_END_',
                            'total': '_TOTAL_',
                            subject_type: gettext("Submission")
                        }, true),
                    "lengthMenu": gettext("Show") + ' _MENU_ ' + gettext("Submission"),
                    "emptyTable": gettext("No data available in table")
                },
                "scrollX": true,
                "searching": false,
                "processing": true,
                "serverSide": true,
                "ajax": {
                    url: dataUrl
                },
                "order":[0,"desc"], //submission date
                "columns": columns,
                "initComplete": function (settings, json) {
                    $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
                    $(".paging_dw_pagination").show();
                },
                "drawCallback": function (settings, json) {
                    $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
                },
                "pagingType": "dw_pagination",
                "columnDefs": [{
                    "targets": "media",
                    "data": null,
                    "defaultContent": "<button>Click!</button>"
                }],
                "rowCallback": function (row, data, rowIndex) {
                    var columnsInDataTable = this.dataTableSettings[0].aoColumns;
                    var visibleColumns = $.grep(columnsInDataTable, function (e) {
                            return e.bVisible != false;
                        });
                    $.each(data.media, function (key, value) {
                        var result = $.grep(columnsInDataTable, function (e) {
                            return e.sName == key;
                        });
                        var columnIndex = -1;
                        for(var i =0; i< visibleColumns.length; i++) {
                            if (key == visibleColumns[i].name) {
                                columnIndex = i;
                                break;
                            }
                        }
                        if(columnIndex == -1) {
                            return row;
                        }
                        var html = '';
                        switch (value.type) {
                            case 'image':
                                html = '<img src="' + value.preview_link + '">';
                                html = html + '<br>';
                                html = html + '<a href="' + value.download_link + '">' + value.value + '</a>';
                                break;

                            case 'audio':
                                html = "<audio controls>" +
                                    "<source src='" + value.download_link + "' type='audio/ogg'> \
                                            Your browser does not support the audio tag. \
                                        </audio><br><a href='"+ value.download_link + "'>Download</a>";
                                break;

                            case 'video':
                                html = "<video controls>" +
                                    "<source src='" + value.download_link + "' type='video/mp4'> \
                                            Your browser does not support the audio tag. \
                                        </video><br><a href='"+ value.download_link + "'>Download</a>";
                                break;
                        }
                        $(row).find("td").eq(columnIndex).html(html);
                    });
                    return row;
                }
            });

            this.handleEmptyTable();
        };

        AnalysisPageDataTable.prototype.handleEmptyTable = function () {
            $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
            var isAnyColumnVisible = tableElement.DataTable().columns().visible().reduce(function (a, b) {
                return a || b
            });
            if (!isAnyColumnVisible) {
                $('#analysis_table_empty').show();
                $('.paging_dw_pagination,.dataTables_info,.dataTables_length,.dataTables_scroll').css('visibility', 'hidden');
            } else {
                $('#analysis_table_empty').hide();
                $('.paging_dw_pagination,.dataTables_info,.dataTables_length,.dataTables_scroll').css('visibility', 'visible');
            }
        }
        return AnalysisPageDataTable;
    })($, tableElement);

    $.getJSON(headerUrl, function (columns) {
        analysisTable = new AnalysisPageDataTable(columns);
    });


    /*Col Customization Widget*/

    var ColCustomWidget = (function ($) {
        function ColCustomWidget(customizationHeader) {
            this.$columnWidget = $(".customization-widget");
            this.$custMenu = $(".customization-menu");
            this.$colWidgetActions = $("#cust-icon, .customization-widget-close");
            this.$customizationIcon = $("#cust-icon");
            this.$selectAll = $(".select-all");
            this.$selectNone = $(".select-none");
            this.$customizationOverlay = $(".customization-overlay");
            this.$pageHeader = $("#container_header_application");
            this.$pageContent = $("#container_content");

            this.items = customizationHeader;
            this.init();

            //Bind initial click events
            this.bindEvents();

        }

        ColCustomWidget.prototype.init = function () {
            //Start constructing the widget with loaded Items
            this.constructItems(this.items);

        };

        ColCustomWidget.prototype.bindEvents = function () {

            var self = this;
            var customizationOverlayHeight;

            this.$colWidgetActions.on("click", function () {
                if (self.$customizationIcon.hasClass("active")) {
                    self.$columnWidget.hide();
                    self.$customizationOverlay.hide();
                    self.$customizationIcon.removeClass("active");
                    self.submit();
                } else {
                    self.$columnWidget.show();
                    customizationOverlayHeight = self.$pageHeader.outerHeight() + self.$pageContent.outerHeight() + 30;
                    if(customizationOverlayHeight > 970) {
                        customizationOverlayHeight = customizationOverlayHeight + 5;
                    } else {
                        customizationOverlayHeight = 970;
                    }
                    self.$customizationOverlay.height(customizationOverlayHeight).show();
                    self.$customizationIcon.addClass("active");
                }
            });

            this.$customizationOverlay.on("click", function () {
                self.$columnWidget.hide();
                $(this).hide();
                self.submit();
            });


            /*Column Customisation click events*/
            this.$selectAll.on("click", function () {
                self.$custMenu.find("input[type=checkbox]").prop('checked', true);
                self.handleVisibility();
            });

            this.$selectNone.on("click", function () {
                self.$custMenu.find("input[type=checkbox]").prop('checked', false);
                self.handleVisibility();
            });

            $(".customization-menu input[type=checkbox]").click(function (event) {
                self.handleCheckBoxes(this, event);
                event.stopPropagation();
            });

            $(".customization-menu span").on("click", function (event) {
                var $checkBox = $(this).prev("input[type=checkbox]");
                $checkBox[0].checked = !$checkBox[0].checked;
                self.handleCheckBoxes($checkBox[0], event);
                event.stopPropagation();
            });
        };

        ColCustomWidget.prototype.handleCheckBoxes = function(element, event) {
            var self = this;

            if (element.checked) {
                $(element).parents('li').children('input[type=checkbox]').prop('checked', true);
            }

            if($(element).parent("ul").length == 0) {

                var $parentElement =$(element).closest("ul"),
                    $listElements = $parentElement.children("li"),
                    $inputElementsLength = $listElements.find("input[type=checkbox]").length;

                if($listElements.find("input:checkbox:checked").length != $inputElementsLength) {
                    $parentElement.find("> input:checkbox").prop('checked', false);
                } else {
                    $parentElement.find("> input:checkbox").prop('checked', true);
                }

            }

            $(element).parent().find('input[type=checkbox]').prop('checked', element.checked);
            self.handleVisibility(element);
            event.stopPropagation();
        };

        ColCustomWidget.prototype.handleVisibility = function (element) {
            var self = this;

            //Recursively handle all column visibility
            if (!element) {
                self.$custMenu.find("input[type=checkbox]").each(function (index, element) {
                    self.handleVisibility(element);
                });
                return;
            }

            $(element).parent().find('li > input[type=checkbox]').each(function (index, elem) {
                self.handleVisibility(elem);
            });
            self.updateTable(element.name, element.checked);
            analysisTable.handleEmptyTable();
        };

        ColCustomWidget.prototype.updateTable = function (columnName, visibility) {
            column = tableElement.DataTable().column(columnName + ':name');
            column.visible(visibility);
            tableElement.DataTable().draw('page');
        };

        ColCustomWidget.prototype.constructItems = function (customizationHeader) {
            var self = this;
            $.each(customizationHeader, function (index, value) {
                var $newParentElement = self.createColItems("ul", value, self.$custMenu);

                if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                    self.iterateItems(value.children, $newParentElement);
                }
            });
        };

        ColCustomWidget.prototype.createColItems = function (element, value, parentElement) {
            var $listElement = $('<' + element + '/>'),
                $checkBox = $("<input type='checkbox' value='True' name='" + value.data + "'>");

            $checkBox.prop('checked', value.visibility);
            $listElement.append("<span title='" + value.title + "'>" + value.title + "</span>").prepend($checkBox);
            parentElement.append($listElement);

            return $listElement;
        };

        ColCustomWidget.prototype.iterateItems = function (items, $parentElement) {
            var self = this;
            $.each(items, function (index, value) {
                if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                    var $newParentElement = self.createColItems("ul", value, $parentElement);
                    self.constructChildNodes(value, $newParentElement);
                } else {
                    self.constructChildNodes(value, $parentElement);
                }
            });
        };

        ColCustomWidget.prototype.constructChildNodes = function (value, $parentElement) {
            if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                this.iterateItems(value.children, $parentElement);
            } else {
                this.createColItems("li", value, $parentElement);
            }
        };

        ColCustomWidget.prototype.submit = function () {
            $.ajax({
                type: "POST",
                url: preferenceUrl,
                data: $("#customization-form").serialize(),
                success: self.submitSuccess,
                dataType: 'json'
            });
        };

        ColCustomWidget.prototype.submitSuccess = function () {
            //reload the table
            //TODO
        };

        return ColCustomWidget;
    })($);

    $.getJSON(preferenceUrl, function (customizationHeader) {
        colCustomization = new ColCustomWidget(customizationHeader);
    });

});
