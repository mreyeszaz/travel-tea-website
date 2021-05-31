// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        post_list: [],
        user: -1,
        thumbnail: "",
        bio: "",
        edit_bio: false,
        new_bio: "",
    };

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
                });
            });

            reader.readAsDataURL(file);
        }
    };

    app.delete_profilepic = function(){
        axios.post(delete_profilepic_url);
        app.vue.thumbnail = "";
    };


    app.delete_post = function(p_idx) {
        let id = p_idx;
        axios.get(delete_post_url, {params: {id: id}})
        .then(function (response) {
            for (let i = 0; i < app.vue.post_list.length; i++) {
                if (app.vue.post_list[i].id === id) {
                    app.vue.post_list.splice(i, 1);
                    break;
                }
            }
        });
    };

    app.set_edit_bio = function(new_value){
        app.vue.edit_bio = new_value;
    }

    app.add_bio = function(){
        app.vue.bio = app.vue.new_bio;
        axios.post(add_bio_url,{
            bio: app.vue.bio
        });
        app.cancel_bio();
    }

    app.cancel_bio = function(){
        app.vue.new_bio = "";
        app.vue.edit_bio = false;
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        upload_file: app.upload_file,
        delete_profilepic: app.delete_profilepic,
        delete_post: app.delete_post,
        add_bio: app.add_bio,
        cancel_bio: app.cancel_bio,
        set_edit_bio: app.set_edit_bio,
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
            //all getting added as arrays instead of single variables??
            app.vue.thumbnail = result.data.tl;
            app.vue.user = result.data.uid;
            app.vue.bio = result.data.bio;
        });

        axios.get(get_posts_url)
        .then(function(result){
            let posts = result.data.posts;
            for(let i = 0; i < posts.length; i++) {
                if(posts[i].user == app.vue.user){ //if user id from post matches current user id
                    app.vue.post_list.push({
                        id: posts[i].id,
                        title: posts[i].title,
                        post_text: posts[i].post_text,
                        image: posts[i].image,
                        username: posts[i].username,
                        email: posts[i].email,
                        country: posts[i].country,
                        overall: posts[i].overall,
                        beach: posts[i].beach,
                        sights: posts[i].sights,
                        food: posts[i].food,
                        night: posts[i].night,
                        shop: posts[i].shop,
                    });
                }
            }
        });

    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
