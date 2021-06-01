// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        post_list: [],
        country: "",
        country_id: null,

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

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        delete_post: app.delete_post,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target-country-profile",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(get_country_url)
        .then(function (result) {
            app.vue.country = result.data.country_name;
            app.vue.country_id = result.data.country_id;

        });

        axios.get(get_posts_url)
        .then(function(result){
            let posts = result.data.posts;
            for(let i = 0; i < posts.length; i++) {
                if(posts[i].place_country == app.vue.country){ //if country name from post matches current user id
                    app.vue.post_list.push({
                        id: posts[i].id,
                        title: posts[i].title,
                        post_text: posts[i].post_text,
                        image: posts[i].image,
                        username: posts[i].username,
                        email: posts[i].email,
                        overall: posts[i].overall,
                        beach: posts[i].beach,
                        sights: posts[i].sights,
                        food: posts[i].food,
                        night: posts[i].night,
                        shop: posts[i].shop,
                        place: posts[i].place,
                        place_name: posts[i].place_name,
                        place_address: posts[i].place_address,
                        place_city: posts[i].place_city,
                        place_state: posts[i].place_state,
                        place_kind: posts[i].place_kind,
                        place_country: posts[i].place_country,
                        place_properties: posts[i].place_properties,
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