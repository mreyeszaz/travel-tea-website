// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        thumbnail: "",
        //thumbnail_list: [],
    };

    /*app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };*/

    /*app.add_thumbnail = function(){
        axios.post(add_thumbnail_url,{
            thumbnail: app.vue.thumbnail
        })
        .then(function(response){
            app.vue.thumbnail_list.push({
                id: response.data.id,
                email: response.data.email,
                thumbnail: app.vue.thumbnail
            });
        });
        app.vue.thumbnail = "";
    }*/

    app.upload_file = function(event){
        let input = event.target; //reference to input object that triggers event
        let file = input.files[0]; //select single file to upload
        if(file){ //makes sure file is actually there
            let reader = new FileReader();
            reader.addEventListener("load", function(){
                //send image to server
                app.vue.thumbnail = reader.result;
                axios.post(upload_thumbnail_url, {
                    tl: app.vue.thumbnail
                });//.then(function(response){
                    //set local preview
                    //app.vue.thumbnail=reader.result;
                    /*
                    app.vue.thumbnail_list.push({
                        id: response.data.id,
                        email: response.data.email,
                        thumbnail: app.vue.thumbnail,
                    });*/
                });

            reader.readAsDataURL(file);
            }
            //app.vue.thumbnail = "";

            /*app.vue.uploading = true;
            let file_type = file.type;
            let file_name = file.name;
            let full_url = file_upload_url + "&file_name=" + encodeURIComponent(file_name)
                + "&file_type=" + + encodeURIComponent(file_type);
            let req = new XMLHttpRequest();
            req.addEventListener("load", function(){
                app.upload_complete(file_name, file_type);
            });
            req.open("PUT", full_url, true);
            req.send(file); //uploads file to website*/
        };
    //};

    app.delete_profilepic = function(){
        axios.post(delete_profilepic_url);
        app.vue.thumbnail = "";
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        upload_file: app.upload_file,
        delete_profilepic: app.delete_profilepic,
        //add_thumbnail: app.add_thumbnail,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target-profile",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(get_profile_url)
        .then(function(result){
            //let users = result.data.users;
            //app.enumerate(users);
            app.vue.thumbnail = result.data.tl;
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
