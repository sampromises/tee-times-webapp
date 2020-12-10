const enableLoadingButton = () => {
  $("#submit-button").prop("disabled", true);
  $("#submit-button").text("Loading...");
};

const enableSubmitButton = () => {
  $("#submit-button").prop("disabled", false);
  $("#submit-button").text("Submit");
};

$(document).ready(function () {
  // On form submission ...
  $("form").on("submit", function () {
    console.log("Form has been submitted.");
    enableLoadingButton();

    // Gather form input
    const earliestTime = $('input[name="earliest-time"]').val();
    const latestTime = $('input[name="latest-time"]').val();
    const daysAhead = $('input[name="days-ahead"]').val();
    const courses = $("#courses-form input:checkbox:checked")
      .map(function () {
        return this.name;
      })
      .get();
    console.log(earliestTime, latestTime, daysAhead, courses);

    $.ajax({
      type: "POST",
      url: "/tee_times",
      data: {
        earliest_time: earliestTime,
        latest_time: latestTime,
        days_ahead: daysAhead,
        courses: courses,
      },
      success: function (results) {
        enableSubmitButton();

        const resultsContainer = document.createElement("div");
        const header = document.createElement("h1");
        header.innerText = "Tee times found:";
        resultsContainer.appendChild(header);

        for (let course in results) {
          let courseHeader = document.createElement("h2");
          courseHeader.innerText = course;
          resultsContainer.appendChild(courseHeader);

          let teeTimeList = document.createElement("ul");
          if (results[course].length > 0) {
            for (let teeTime of results[course]) {
              let teeTimeItem = document.createElement("li");
              teeTimeItem.innerText = teeTime;
              teeTimeList.appendChild(teeTimeItem);
            }
          } else {
            let noneFoundText = document.createElement("li");
            noneFoundText.innerText = "None found. 😔";
            teeTimeList.appendChild(noneFoundText);
          }
          resultsContainer.appendChild(teeTimeList);
        }

        $("#results").html(resultsContainer);
      },
      error: function (error) {
        console.log(error);
        $("#results").html(error);
      },
    });
  });
});
