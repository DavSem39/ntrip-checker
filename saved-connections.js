/*
=================================================
NTRIP CHECKER
Saved Connections Module
=================================================
*/

function saveConnection(){

    let profiles =
        JSON.parse(
            localStorage.getItem("ntripProfiles")
            || "[]"
        );

    let profile = {

        host:
            document.getElementById("host").value,

        port:
            document.getElementById("port").value,

        username:
            document.getElementById("username").value,

        password:
            document.getElementById("password").value

    };

    profiles.push(profile);

    localStorage.setItem(
        "ntripProfiles",
        JSON.stringify(profiles)
    );

    populateProfiles();

    alert("Connection saved successfully.");

}


function populateProfiles(){

    let profiles =
        JSON.parse(
            localStorage.getItem("ntripProfiles")
            || "[]"
        );

    let dropdown =
        document.getElementById(
            "savedConnections"
        );

    if(!dropdown)
        return;

    dropdown.innerHTML = "";

    profiles.forEach((profile,index)=>{

        dropdown.innerHTML +=
        `<option value="${index}">
            ${profile.host}
            (${profile.username})
        </option>`;

    });

}


function loadConnection(){

    let profiles =
        JSON.parse(
            localStorage.getItem("ntripProfiles")
            || "[]"
        );

    let dropdown =
        document.getElementById(
            "savedConnections"
        );

    if(!dropdown)
        return;

    let index = dropdown.value;

    let profile =
        profiles[index];

    if(!profile)
        return;

    document.getElementById("host").value =
        profile.host;

    document.getElementById("port").value =
        profile.port;

    document.getElementById("username").value =
        profile.username;

    document.getElementById("password").value =
        profile.password;

}


function deleteConnection(){

    let profiles =
        JSON.parse(
            localStorage.getItem("ntripProfiles")
            || "[]"
        );

    let dropdown =
        document.getElementById(
            "savedConnections"
        );

    if(!dropdown)
        return;

    let index =
        parseInt(dropdown.value);

    if(isNaN(index))
        return;

    profiles.splice(index,1);

    localStorage.setItem(
        "ntripProfiles",
        JSON.stringify(profiles)
    );

    populateProfiles();

}


window.onload = function(){

    populateProfiles();

};
