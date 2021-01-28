function compile_button() {
                $.ajax({
                    type: 'POST',
                    url: '/compile',
                    cache: false,
                    success: function(data, status, request) {
                        status_url = data['Location']
                        get_task_state(status_url);
                        message = data['message'];
                        alert(message);
                        $('#start-compile').attr("disabled", true)
                        //alert(status_url);
                    },
                    error: function() {
                        alert('Unexpected error');
                    }
                 });
            }


function get_task_state(status_url) {
                $.getJSON(status_url, function(data) {
                    // task not finish
                    if ( data['state'] == 'PENDING' || data['state'] == 'PROGESS' ){
                        $('#task_message').text(data['Status']);
                        setTimeout(function() {
                            get_task_state(status_url);
                        }, 2000);
                    }
                    // task finish (FAILURE or SUCCESS or others...)
                    else {
                        if ( data['Status'] != 'All done!' ) {
                            $('#task_message').text('Something go wrong: ' + data['Status']);
                        }
                        else {
                            $('#task_message').text(data['Status']);
                        }
                        $('#start-compile').attr("disabled", false)
                    }
                });
            }
