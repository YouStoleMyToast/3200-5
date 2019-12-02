local = "http://localhost:8080/"
hrkURL = "https://nameless-anchorage-27924.herokuapp.com/"


const load = () => {
    checkCookie()
}
window.onload = load

var newEventName = document.querySelector("#newEventName"),
    newEventDate = document.querySelector("#newEventDate"),
    newEventSubject = document.querySelector("#newEventSubject"),
    newEventDetails = document.querySelector("#newEventDetails"),
    createEventButton = document.querySelector("#createEventButton");

createEventButton.onclick = function(){
    var name = newEventName.value,
        date = newEventDate.value,
        subject = newEventSubject.value,
        details = newEventDetails.value;

    var encodedData = "name=" + encodeURIComponent(name) + "&date=" + encodeURIComponent(date) + "&subject=" + encodeURIComponent(subject) + "&details=" + encodeURIComponent(details);

    fetch(`${hrkURL}events`, {
        method: 'POST',
        body: encodedData,
        credentials: 'include',
        headers: {
            "Content-type": "application/x-www-form-urlencoded"
        }
    }).then(function(response){
        console.log(response.status,"POST")
        if (response.status === 401){
            openPopup("login","You Must Sign In First")
        }else{
            newEventName.value = "";
            newEventDate.value = "";
            newEventSubject.value = "";
            newEventDetails.value = "";
            getEvents()
        }
    })
}

function getEvents(){
    fetch(`${hrkURL}events`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }).then(function(response){
        console.log(response.status,"GET")
        if (response.status === 401){
            openPopup("login","You Must Sign In To View Events")
        }else{
            return response.json()
        }
        // return response.json()
    }).then(function(data){
        document.querySelector("#eventList").innerHTML = "";
        data.forEach(function(event){
            var id = event.id,
                name = event.name,
                date = event.date,
                subject = event.subject,
                details = event.details;

            var newItem = document.createElement("div"),
                nameDiv = document.createElement("div"),
                dateDiv = document.createElement("div"),
                subjectDiv = document.createElement("div"),
                detailsDiv = document.createElement("div"),
                editButton = document.createElement("button"),
                deleteButton = document.createElement("button");

            newItem.className = "eventItem";
            nameDiv.className = "eventItemElement";
            dateDiv.className = "eventItemElement";
            subjectDiv.className = "eventItemElement";
            detailsDiv.className = "eventItemElement";
            editButton.className = "eventItemButton";
            deleteButton.className = "eventItemButton";
            nameDiv.id = "eventName";
            dateDiv.id = "eventDate";
            subjectDiv.id = "eventSubject";
            detailsDiv.id = "eventDetails";
            editButton.id = "eventEditButton";
            deleteButton.id = "eventDeleteButton";

            nameDiv.innerHTML = `Name: ${name}`;
            dateDiv.innerHTML = `Date: ${date}`;
            subjectDiv.innerHTML = `Subject: ${subject}`;
            detailsDiv.innerHTML = `Details: ${details}`;
            editButton.innerHTML = "Edit";
            deleteButton.innerHTML = "Delete";

            deleteButton.onclick = function () {
                var proceed = confirm(`DELETE ${name}?`);
                if (proceed) {
                    console.log(id)
                    fetch(`${hrkURL}events/${id}`, {
                        method: 'DELETE',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }
                    }).then(function () {
                        console.log("Event Deleted")
                        getEvents()
                    });
                };
            };

            editButton.onclick = function(){
                var editName = document.createElement("input"),
                    editDate = document.createElement("input"),
                    editSubject = document.createElement("input"),
                    editDetails = document.createElement("input"),
                    updateButton = document.createElement("button");

                editName.className = "newEventItemElement";
                editDate.className = "newEventItemElement";
                editSubject.className = "newEventItemElement";
                editDetails.className = "newEventItemElement";
                updateButton.className = "eventItemButton"
                editName.id = "editName";
                editDate.id = "editDate";
                editSubject.id = "editSubject";
                editDetails.id = "editDetails";
                updateButton.id = "eventUpdateButton";

                editName.value = `${name}`;
                editDate.value = `${date}`;
                editSubject.value = `${subject}`;
                editDetails.value = `${details}`;
                updateButton.innerHTML = "Update";

                newItem.removeChild(nameDiv)
                newItem.removeChild(dateDiv)
                newItem.removeChild(subjectDiv)
                newItem.removeChild(detailsDiv)
                newItem.removeChild(editButton)
                newItem.removeChild(deleteButton)
                
                newItem.appendChild(editName)
                newItem.appendChild(editDate)
                newItem.appendChild(editSubject)
                newItem.appendChild(editDetails)
                newItem.appendChild(updateButton)

                updateButton.onclick = function () {
                    updatedName = document.querySelector("#editName").value;
                    updatedDate = document.querySelector("#editDate").value;
                    updatedSubject = document.querySelector("#editSubject").value;
                    updatedDetails = document.querySelector("#editDetails").value;
                    var encodedData = "name=" + encodeURIComponent(updatedName);
                    encodedData += "&subject=" + encodeURIComponent(updatedSubject);
                    encodedData += "&date=" + encodeURIComponent(updatedDate);
                    encodedData += "&details=" + encodeURIComponent(updatedDetails);
                    fetch(`${hrkURL}events/${id}`, {
                        method: 'PUT',
                        body: encodedData,
                        credentials: 'include',
                        headers: {
                            "Content-type": "application/x-www-form-urlencoded"
                        }
                    }).then(function () {
                        newItem.removeChild(editName)
                        newItem.removeChild(editDate)
                        newItem.removeChild(editSubject)
                        newItem.removeChild(editDetails)
                        newItem.removeChild(updateButton)
                        getEvents();
                    });
                };   
            };
            var eventlist = document.querySelector("#eventList")
            newItem.appendChild(nameDiv)
            newItem.appendChild(dateDiv)
            newItem.appendChild(subjectDiv)
            newItem.appendChild(detailsDiv)
            newItem.appendChild(editButton)
            newItem.appendChild(deleteButton)
    
            eventlist.appendChild(newItem)
        });
    });

};

var loginPopup = document.querySelector("#login_popup"),
    overlay = document.querySelector("#overlay"),
    loginCaption = document.querySelector("#loginCaption"),
    loginEmail = document.querySelector("#loginEmail"),
    loginPassword = document.querySelector("#loginPassword"),
    loginButton = document.querySelector("#loginButton"),
    newAccountButton = document.querySelector("#newAccountButton"),
    navLoginButton = document.querySelector("#navLoginButton"),
    navNewAccountButton = document.querySelector("#navNewAccountButton");

var createPopup = document.querySelector("#create_popup"),
    overlay2 = document.querySelector("#overlay2"),
    createCaption = document.querySelector("#createCaption"),
    userFirstName = document.querySelector("#userFirstName"),
    userLastName = document.querySelector("#userLastName"),
    newLoginEmail = document.querySelector("#newLoginEmail"),
    newLoginPassword = document.querySelector("#newLoginPassword"),
    passwordConfirm = document.querySelector("#passwordConfirm"),    
    createAccountButton = document.querySelector("#createAccountButton");

function openPopup(choice,caption){
    closePopup()
    if (choice == "login"){
        loginCaption.innerHTML = `${caption}`;
        loginPopup.style.display = "block";
    }else{
        createCaption.innerHTML = `${caption}`;
        createPopup.style.display = "block";
    }
}
function closePopup(){
    loginCaption.innerHTML = "",createCaption.innerHTML = "";
    createPopup.style.display = "none",loginPopup.style.display = "none";
}

overlay.onclick = function(){
    closePopup()
}
overlay2.onclick = function(){
    closePopup()
}

newAccountButton.onclick = function(){
    openPopup("create","")
}
navLoginButton.onclick = function(){
    openPopup("login","")
}
navNewAccountButton.onclick = function(){
    openPopup("create","")
}

loginButton.onclick = function(){
    closePopup()
    email = loginEmail.value,password = loginPassword.value;
    encodedData = "email=" + encodeURIComponent(email) + "&password=" + encodeURIComponent(password);
    fetch(`${hrkURL}session`, {
        body: encodedData,
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    }).then(function(response){
        if (response.status == "201"){
            console.log("login Success")
            return response.json()
        }else{
            loginPassword.value = "";
            openPopup("login","Check Your Credentials And Try Again")
        }
    }).then(function(data){
        LoggedInUser(data)
    })
}

createAccountButton.onclick = function(){
    closePopup()
    firstName = userFirstName.value,lastName = userLastName.value,email = newLoginEmail.value,password = newLoginPassword.value,password2 = passwordConfirm.value;
    if (password != password2) {
        newLoginPassword.value = "",passwordConfirm.value = "";
        openPopup("create","Your Passwords Didn't Match")
    }else{
        encodedData = 'firstName=' + encodeURIComponent(firstName) + '&lastName=' + encodeURIComponent(lastName) + '&email=' + encodeURIComponent(email) + '&password=' + encodeURIComponent(password);
        fetch(`${hrkURL}users`, {
            body: encodedData,
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(function (response) {
            if (response.status === 201) {
                return response.json()
            } else if (response.status === 409) {
                console.log('Exists')
                openPopup("login", "Looks Like You Already Have An Account")
            }
        }).then(function(data){
            LoggedInUser(data)

        })
    }
}

function LoggedInUser(data){
    firstName = data.firstName;
    var nav = document.querySelector("#navContainer")
    navLoginButton.style.display = "none",navNewAccountButton.style.display = "none";

    document.querySelector("#welcomeMessage").innerHTML = `hello, ${data.firstName}`
    welcomeMessage.style.display = "block";

    var logOutButton = document.querySelector("#logoutButton");
    logOutButton.style.display = "block";
    nav.appendChild(logOutButton)

    logOutButton.onclick = function(){
        fetch(`${hrkURL}session`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        }).then(function () {
            navLoginButton.style.display = "block";
            navNewAccountButton.style.display = "block";
            welcomeMessage.style.display = "none";
            logOutButton.style.display = "none";
            document.querySelector("#eventList").innerHTML = "";
        });
    }
    getEvents()

}


function checkCookie() {
    console.log("check cookie")
    fetch(`${hrkURL}me`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    }).then(function (response) {
        console.log("res from cookie:", response)
        if (response.status === 200) {
            return response.json();
        };
    }).then(function(data){        
        LoggedInUser(data)
    })
};





