function drawHoursCircle(id, percentage) {
    var circle = new ProgressBar.Circle(id, {
        color: '#aaa',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 4,
        trailWidth: 1,
        easing: 'easeInOut',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: { color: '#FFEA82', a: 0, width: 3 },
        to: { color: '#ED6A5A', a: 1, width: 3 },
        // Set default step function for all animate calls
        step: function(state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);

            var value = Math.round(circle.value() * 25);

            if (value === 0) {
                circle.setText('');
            } else {
                circle.setText(value + " hrs/week");
            }
        }
    });
    circle.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    circle.text.style.fontSize = '1.3rem';
    circle.animate(percentage);
}


function drawQualityCircle(id, percentage) {
    var circle = new ProgressBar.Circle(id, {
        color: '#aaa',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 4,
        trailWidth: 1,
        easing: 'easeInOut',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: { color: '#ED6A5A', a: 1, width: 3 },
        to: { color: '#FFEA82', a: 0, width: 3 },
        // Set default step function for all animate calls
        step: function(state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);

            var value = Math.round(circle.value() * 50) / 10;

            if (value === 0) {
                circle.setText('');
            } else {
                circle.setText(value + " / 5.0");
            }
        }
    });
    circle.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    circle.text.style.fontSize = '1.3rem';
    circle.animate(percentage);
}