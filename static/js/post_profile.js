// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        add_mode: false,
        new_title: "",
        new_post_text: "",
        post_list: [],
        image: "",
        place: "",
        place_properties: null,
        place_type: "",
        selection_done: false,
        overall_rating: 0,
        beach_rating: 0,
        sights_rating: 0,
        food_rating: 0,
        night_rating: 0,
        shop_rating: 0,
        num_posts: 0,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.set_num_like = function(p_idx, value){
        app.vue.post_list[p_idx].num_like = value;
    }

    app.set_num_dislike = function(p_idx, value){
        app.vue.post_list[p_idx].num_dislike = value;
    }

    app.set_num_travel = function(p_idx, value){
        app.vue.post_list[p_idx].num_travel = value;
    }

    app.file = null;

    app.select_file = function(event){
        let input = event.target; //reference to input object that triggers event
        app.file = input.files[0]; //select single file to upload
        if(app.file){ //makes sure file is actually there
            app.vue.selection_done = true;
            let reader = new FileReader();
            reader.addEventListener("load", function(){
                //send image to server
                app.vue.image = reader.result;
            });
            reader.readAsDataURL(app.file);
        }
    };

    // Adds a new post to the database using a request object
    app.add_post = function(){
        //app.select_country();
        axios.post(add_post_url,{
            //put correct info into the database
            title: app.vue.new_title,
            post_text: app.vue.new_post_text,
            image: app.vue.image,
            place: app.vue.place,
            place_properties: app.vue.place_properties,
            place_type: app.vue.place_type,
            overall: app.vue.overall_rating,
            beach: app.vue.beach_rating,
            sights: app.vue.sights_rating,
            food: app.vue.food_rating,
            night: app.vue.night_rating,
            shop: app.vue.shop_rating,
        }).then(function(response){
            // This information is only for the immediate added post
            // This is so that the information is visible right after posting
            app.vue.post_list.push({
                id: response.data.id,
                title: app.vue.new_title,
                post_text: app.vue.new_post_text,
                image: app.vue.image,
                place: app.vue.place,
                place_name: response.data.place_name,
                place_address: response.data.place_address,
                place_city: response.data.place_city,
                place_state: response.data.place_state,
                place_kind: response.data.place_kind,
                place_country: response.data.place_country,
                country_id: response.data.cid,
                place_properties: app.vue.place_properties,
                overall: app.vue.overall_rating,
                beach: app.vue.beach_rating,
                sights: app.vue.sights_rating,
                food: app.vue.food_rating,
                night: app.vue.night_rating,
                shop: app.vue.shop_rating,
                username: response.data.name,
                email: response.data.email,
                liked: 0,
                like_id: -1,
                hover: false,
                likers: [],
                dislikers: [],
                traveled: 0,
                travel_id: -1,
                travel_hover: false,
                travelers: [],
                num_dislike: 0,
                num_like: 0,
                num_travel: 0,
                time: response.data.time,
            });
            app.enumerate(app.vue.post_list);
            app.vue.selection_done = false;
            app.cancel_post();
            app.vue.num_posts = app.vue.post_list.length;
        });
        
        console.log(app.vue.place);
        console.log(app.vue.place_properties);
    };

    app.like_post = function (post_idx, curr_user) {
        let post = app.vue.post_list[post_idx];
        // no like exists, add it
        if(post.liked == 0) {
            app.set_num_like(post_idx, post.num_like+1);
            axios.post(
                add_like_url,
                {
                    is_like: true,
                    post: post.id,
                    num_like: post.num_like,
                    num_dislike: post.num_dislike,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.post_list.length; i++) {
                    if(app.vue.post_list[i].id === post.id) {
                        app.vue.post_list[i].liked = 1;
                        app.vue.post_list[i].like_id = response.data.id;
                        app.vue.post_list[i].likers.push(curr_user);
                        break;
                    }
                }
            });
        }
        // Already liked, unlike
        else if(post.liked == 1) {
            app.set_num_like(post_idx, post.num_like-1);
            axios.post(
                delete_like_url,
                {
                id: post.like_id,
                post: post.id,
                num_like: post.num_like,
                num_dislike: post.num_dislike,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.post_list.length; i++) {
                    if(app.vue.post_list[i].id === post.id) {
                        app.vue.post_list[i].liked = 0;
                        app.vue.post_list[i].like_id = -1;
                        app.vue.post_list[i].likers.splice(app.vue.post_list[i].likers.indexOf(curr_user), 1);
                        break;
                    }
                }
            });
        }
        // Disliked, flip to like
        else {
            app.set_num_like(post_idx, post.num_like+1);
            app.set_num_dislike(post_idx, post.num_dislike-1);
            axios.post(
                flip_like_url,
                {
                    id: post.like_id,
                    is_like: true,
                    post: post.id,
                    num_like: post.num_like,
                    num_dislike: post.num_dislike,
                }
                ).then(function (response) {
                    for(let i = 0; i < app.vue.post_list.length; i++) {
                        if(app.vue.post_list[i].id === post.id) {
                            app.vue.post_list[i].liked = 1;
                            app.vue.post_list[i].dislikers.splice(app.vue.post_list[i].dislikers.indexOf(curr_user), 1);
                            app.vue.post_list[i].likers.push(curr_user);
                            break;
                        }
                    }
                });
        }
    }

    app.dislike_post = function (post_idx, curr_user) {
        let post = app.vue.post_list[post_idx];
        
        // no like exists, add it
        if(post.liked == 0) {
            app.set_num_dislike(post_idx, post.num_dislike+1);
            axios.post(
                add_like_url,
                {
                    is_like: false,
                    post: post.id,
                    num_like: post.num_like,
                    num_dislike: post.num_dislike,
                }
                ).then(function (response) {
                    for(let i = 0; i < app.vue.post_list.length; i++) {
                        if(app.vue.post_list[i].id === post.id) {
                            app.vue.post_list[i].liked = -1;
                            app.vue.post_list[i].like_id = response.data.id;
                            app.vue.post_list[i].dislikers.push(curr_user);
                            break;
                        }
                    }
                });
            }
            // Already liked, flip to dislike
            else if(post.liked == 1) {
                app.set_num_like(post_idx, post.num_like-1);
                app.set_num_dislike(post_idx, post.num_dislike+1);
                axios.post(
                    flip_like_url,
                    {
                        id: post.like_id,
                        is_like: false,
                        post: post.id,
                        num_like: post.num_like,
                        num_dislike: post.num_dislike,
                    }
                    ).then(function (response) {
                        for(let i = 0; i < app.vue.post_list.length; i++) {
                            if(app.vue.post_list[i].id === post.id) {
                                app.vue.post_list[i].liked = -1;
                                app.vue.post_list[i].likers.splice(app.vue.post_list[i].likers.indexOf(curr_user), 1);
                                app.vue.post_list[i].dislikers.push(curr_user);
                                
                                break;
                            }
                        }
                    });
                }
                // Already disliked, toggle off
                else {
                    app.set_num_dislike(post_idx, post.num_dislike-1);
                    axios.post(
                        delete_like_url,
                        {
                            id: post.like_id,
                            post: post.id,
                            num_like: post.num_like,
                            num_dislike: post.num_dislike,
                        }
                        ).then(function (response) {
                            for(let i = 0; i < app.vue.post_list.length; i++) {
                                if(app.vue.post_list[i].id === post.id) {
                                    app.vue.post_list[i].liked = 0;
                                    app.vue.post_list[i].like_id = -1;
                                    app.vue.post_list[i].dislikers.splice(app.vue.post_list[i].dislikers.indexOf(curr_user), 1);
                                    break;
                                }
                            }
                        });
                    }
                    
                }
                
    app.travel_post = function (post_idx, curr_user) {
        let post = app.vue.post_list[post_idx];

        // no like exists, add it
        if(post.traveled == 0) {
            app.set_num_travel(post_idx, post.num_travel+1);
            axios.post(
                add_travel_url,
                {
                    has_traveled: true,
                    post: post.id,
                    num_travel: post.num_travel,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.post_list.length; i++) {
                    if(app.vue.post_list[i].id === post.id) {
                        app.vue.post_list[i].traveled = 1;
                        app.vue.post_list[i].travel_id = response.data.id;
                        app.vue.post_list[i].travelers.push(curr_user);
                        break;
                    }
                }
            });
        }
        // Already liked, unlike
        else if(post.traveled == 1) {
            app.set_num_travel(post_idx, post.num_travel-1);
            axios.post(
                delete_travel_url,
                {
                id: post.travel_id,
                post: post.id,
                num_travel: post.num_travel,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.post_list.length; i++) {
                    if(app.vue.post_list[i].id === post.id) {
                        app.vue.post_list[i].traveled = 0;
                        app.vue.post_list[i].travel_id = -1;
                        app.vue.post_list[i].travelers.splice(app.vue.post_list[i].travelers.indexOf(curr_user), 1);
                        break;
                    }
                }
            });
        }
    }

    app.get_liker_string = function (p_idx) {
        let post = app.vue.post_list[p_idx];
        let s = "";
        for(let i = 0; i < app.vue.post_list[p_idx].likers.length; i++) {
            if(i == 0) {
                s += "Liked by ";
            }
            s+= post.likers[i];
            s+= ", ";
        }
        // Remove last 2 chars of string
        if(s !== "") {
            s = s.slice(0, -2);
        }

        let j = 0;

        for(; j < post.dislikers.length; j++) {
            if(j == 0) {
                if(s !== "") {
                    s += "; ";
                }
                s += "Disliked by ";
            }
            s+= post.dislikers[j];
            s+= ", ";
        }

        if(j > 0) {
            s = s.slice(0, -2);
        }
        return s;
    }

    app.get_traveler_string = function (p_idx) {
        let post = app.vue.post_list[p_idx];
        let s = "";
        for(let i = 0; i < app.vue.post_list[p_idx].travelers.length; i++) {
            if(app.vue.post_list[p_idx].travelers.length == 1){
                s+= post.travelers[i];
                s += " has also traveled here";
            }
            else if(app.vue.post_list[p_idx].travelers.length >= 2) {
                if(i == app.vue.post_list[p_idx].travelers.length-2) {
                    s+= post.travelers[i];
                    s += " and ";
                }
                else{
                s+= post.travelers[i];
                s+= ", ";
                }
                if(i == app.vue.post_list[p_idx].travelers.length-1) {
                    s = s.slice(0, -2);
                    s += " have also traveled here";
                }
            }
        }
        return s;
    }

    app.set_hover = function (p_idx, new_value) {
        app.vue.post_list[p_idx].hover = new_value;
    }

    app.travel_hover = function (p_idx, new_value) {
        app.vue.post_list[p_idx].travel_hover = new_value;
    }

    app.cancel_post = function(){
        app.vue.add_mode = false;
        app.vue.new_post_text = "";
        app.vue.new_title = "";
        app.vue.image = "";
        app.vue.place = "";
        app.vue.place_properties = null;
        app.vue.place_type = "";
        app.vue.overall_rating = 0;
        app.vue.beach_rating = 0;
        app.vue.sights_rating = 0;
        app.vue.food_rating = 0;
        app.vue.night_rating = 0;
        app.vue.shop_rating = 0;
        document.querySelector('#geocoder-container').style.display = 'none';
        document.querySelector('#location-search').style.display = 'none';
        document.querySelector('#btn-mode').style.display = 'block';
        geocoder.clear();
    };

    app.delete_post = function(p_idx) {
        let id = p_idx;
        axios.get(delete_post_url, {params: {id: id}})
        .then(function (response) {
            for (let i = 0; i < app.vue.post_list.length; i++) {
                if (app.vue.post_list[i].id === id) {
                    app.vue.post_list.splice(i, 1);
                    app.enumerate(app.vue.post_list);
                    break;
                }
            }
            app.vue.num_posts = app.vue.post_list.length;
        });
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        add_post: app.add_post,
        cancel_post: app.cancel_post,
        delete_post: app.delete_post,
        like_post: app.like_post,
        dislike_post: app.dislike_post,
        get_liker_string: app.get_liker_string,
        set_hover: app.set_hover,
        travel_post: app.travel_post,
        get_traveler_string: app.get_traveler_string,
        travel_hover: app.travel_hover,
        select_file: app.select_file,
        set_num_like: app.set_num_like,
        set_num_dislike: app.set_num_dislike,
        set_num_travel: app.set_num_travel,

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target-profile-post",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(get_posts_url).then(function(result){
            let post_url = window.location.href;
            let p = post_url.split("/");
            let post_id = p[p.length-1];
            let temp_posts = result.data.posts;
            let posts = [];
            for(let i = 0; i < temp_posts.length; ++i) {
                if(temp_posts[i].id == post_id) {
                    posts.push(temp_posts[i]);
                }
            }
            app.enumerate(posts);
            let temp_likes = result.data.likes;
            let likes = [];
            for(let i = 0; i < temp_likes.length; ++i) {
                if(temp_likes[i]["post"] == post_id) {
                    likes.push(temp_likes[i]);
                }
            }
            let temp_travels = result.data.travels;
            let travels = []
            for(let i = 0; i < temp_travels.length; ++i) {
                if(temp_travels[i]["post"] == post_id) {
                    travels.push(temp_travels[i]);
                }
            }
            for(let i = 0; i < posts.length; i++) {
                posts[i].hover = false;
                posts[i].liked = 0;
                posts[i].like_id = -1;
                for(let j = 0; j < likes.length; j++) {
                    if(likes[j].post == posts[i].id) {
                        posts[i].liked = likes[j].is_like ? 1 : -1;
                        posts[i].like_id = likes[j].id;
                        break;
                    }
                }
            }
            for(let i = 0; i < posts.length; i++) {
                posts[i].travel_hover = false;
                posts[i].traveled = 0;
                posts[i].travel_id = -1;
                for(let j = 0; j < travels.length; j++) {
                    if(travels[j].post == posts[i].id) {
                        posts[i].traveled = travels[j].has_traveled ? 1 : -1;
                        posts[i].travel_id = travels[j].id;
                        break;
                    }
                }
            }

            app.vue.post_list = posts;
            app.vue.num_posts = app.vue.post_list.length;
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
