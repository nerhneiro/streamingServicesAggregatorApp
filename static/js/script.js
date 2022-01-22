function manager(event) {
    event = event || window.event
    var target = event.target || event.srcElement
    songs = document.getElementsByClassName("play-stop-change-color");
    if ('play-stop-icon' === target.id) {
        way = target.src;
        array = way.split("/");
        index = array.length - 1;
        if (array[index] == 'play.svg') {
            play = target.src.split("play.svg")[0];
            play += 'stop.svg';
            target.src = play;
            for (element of songs) {
                if (element != target) {
                    link = element.src;
                    link = link.split('img')[0];
                    link += 'img/play.svg';
                    element.src = link;
                }
            }
        }
        if (array[index] == 'stop.svg') {
            stop = target.src.split("stop.svg")[0];
            stop += 'play.svg';
            target.src = stop;
        }
        return false
    } else if ("song-points-press" === target.id) {
        song_window = target.getElementsByClassName('song-window')[0];
       // if(song_window.style.display == "block") {
       //     song_window.style.display = "none";
       // }
       // else {
       //     song_window.style.display = "block";
       // }
        if (song_window.style.visibility === 'visible') {
            song_window.style.visibility = 'hidden';
        } else {
            song_window.style.visibility = 'visible';
        }
        song_windows = document.getElementsByClassName('song-window');

        for (element of song_windows) {
            if (element !== song_window) {
                element.style.visibility = 'hidden';
            }
        }
    } else {
        windows = document.getElementsByClassName("song-window");
        for (element of windows) {
            element.style.visibility = 'hidden';
        }
    }
}

function visibilityChange() {
    // document.getElementById('sort_by_year_form').style.visibility = "visible";
    // if(document.getElementById('sort_by_year_form').style.visibility === "visible") {
    //     document.getElementById('sort_by_year_form').style.visibility = "hidden";
    // }
    // else {
    //     document.getElementById('sort_by_year_form').style.visibility = "visible";
    // }
    if(document.getElementById('sort_by_year_form').style.display === "block") {
        document.getElementById('sort_by_year_form').style.display = "none";
    }
    else {
        document.getElementById('sort_by_year_form').style.display = "block";
    }
}

function get_additional_information(number) {
    genres = document.getElementById("info");
    controller = document.getElementById("href-info");

    if( genres.style.visibility === "visible" ) {
        genres.style.visibility = "hidden";
        controller.textContent = "и еще " + number + " других" ;
    }
    else {
        genres.style.visibility = "visible";
        controller.textContent = "скрыть";
    }
}