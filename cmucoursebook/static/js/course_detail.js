google.charts.load('current', {packages: ['corechart']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {}		//placeholder for setOnLoadCallback

function drawChartRating(data) {
	var table = new google.visualization.DataTable();
	table.addColumn('string', 'Semester');
	table.addColumn('number', 'Rating');


	for (var key in data) {
		if (data.hasOwnProperty(key)) {
			table.addRows([[key, data[key]]]);
		}
	}

	var options = {title: 'Average Course Rating',
				    legend: 'none',
				    height: 400,
				    lineWidth: 7,
				    vAxis: {
				   		ticks: [0, 1, 2, 3, 4, 5]
				    }};

	var chart = new google.visualization.LineChart(document.getElementById('lineChart'));
	chart.draw(table, options);
}

function drawChartHours(data) {
	var table = new google.visualization.DataTable();
	table.addColumn('string', 'Semester');
	table.addColumn('number', 'Hours');


	for (var key in data) {
		if (data.hasOwnProperty(key)) {
			table.addRows([[key, data[key]]]);
		}
	}

	var options = {title: 'Average Hours Spent',
				    legend: 'none',
				    height: 400,
				    lineWidth: 7,
				    vAxis: {
				   		ticks: [0, 5, 10, 15, 20, 25]
				    }};

	var chart = new google.visualization.LineChart(document.getElementById('lineChart'));
	chart.draw(table, options);
}

function drawChartDifficulty(data) {
	var table = new google.visualization.DataTable();
	table.addColumn('string', 'Difficulty');
	table.addColumn('number', 'Count');

	for (var key in data) {
		if (data.hasOwnProperty(key)) {
			table.addRows([[key, data[key]]]);
		}
	}

	var options = {height: 400}

	var chart = new google.visualization.PieChart(document.getElementById('lineChart'));
	chart.draw(table, options);
}

function getDataRating() {
	$("#lineChart").empty();

	$("#rt").attr('class', 'active');
	$("#ht").removeAttr('class');
	$("#dt").removeAttr('class');

	var cid = $("#course_id").text();
	$.ajax({
		url: "get-course-data",
		data: {'cid': cid, 'type': 'rating'},
		dataType: "json",
		success: drawChartRating
	});
}

function getDataHours() {
	$("#lineChart").empty();

	$("#rt").removeAttr('class');
	$("#ht").attr('class', 'active');
	$("#dt").removeAttr('class');

	var cid = $("#course_id").text();
	$.ajax({
		url: "get-course-data",
		data: {'cid': cid, 'type': 'hours'},
		dataType: "json",
		success: drawChartHours
	});
}

function getDataDifficulty() {
	$("#lineChart").empty();

	$("#rt").removeAttr('class');
	$("#ht").removeAttr('class');
	$("#dt").attr('class', 'active');

	var cid = $("#course_id").text();
	$.ajax({
		url: "get-course-data",
		data: {'cid': cid, 'type': 'difficulty'},
		dataType: "json",
		success: drawChartDifficulty
	});
}

function skillTags() {
	$(".skill-string").each(function() {
		var skills = $(this).val().split(",");
		var length = skills.length;

		for (var i = 0; i < length; i++) {
			$(this).parent().append(
				'<span class="badge badge-pill badge-primary skill">' + 
				skills[i] + 
				'</span>&nbsp;&nbsp;'
			);
		}
	});
}

window.onload = getDataRating;

$(document).ready(function() {
	$("#rating-tab").click(function() {
		getDataRating();
		return false;
	})
	$("#hours-tab").click(function() {
		getDataHours();
		return false;
	});
	$("#difficulty-tab").click(function() {
		getDataDifficulty();
		return false;
	});

	skillTags();
});