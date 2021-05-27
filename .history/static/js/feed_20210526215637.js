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
        new_post_text: "",
        post_list: [],
        posts:[],
    };
    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            // Only user's post are going to be editable so we need to check 
            if(p.email == user_email) {
                p.editable = true;
            } else {
                p.editable = false;
            }
            
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
        }
        return a;
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of app.vue.posts) {
            p._idx = i++;
        }
    };

    app.do_edit = (post_idx) => {
        // Function for edit feature 
        // Need to make sure that no other post is being or can be edited.
        // If so, do nothing.  
        //Otherwise, proceed as below.



        let p = app.vue.posts[post_idx];
        p.edit = true;
        p.is_pending = false;
    };

    app.do_cancel = (post_idx) => {
        // Handler for button that cancels the edit.
        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // If the post has not been saved yet, we delete it.
            app.vue.posts.splice(post_idx, 1);
            app.reindex();
        } else {
            // We go back to before the edit.
            p.edit = false;
            p.is_pending = false;
            p.content = p.original_content;
        }
    };

    app.do_save = (post_idx) => {
        // Handler for "Save edit" button.
        let p = app.vue.posts[post_idx];
        if (p.content !== p.server_content) {
            p.is_pending = true;
            axios.post(posts_url, {
                content: p.content,
                id: p.id,
                is_reply: p.is_reply,
            }).then((result) => {
                console.log("Received:", result.data);
                p.id = result.data.id
                p.edit = false
                p.is_pending = false
                // We will receive the post id (in case it was inserted), and the content.  
                //Both need to be set and make the editing has terminated.
            }).catch(() => {
                p.is_pending = false;
                console.log("Caught error");
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;
            p.original_content = p.content;
        }


    }

/*
    app.add_post = function(){
        axios.post(add_post_url,{
            //put correct post text into the database
            post_text: app.vue.new_post_text,
        }).then(function(response){
            app.vue.post_list.push({
                id: response.data.id,
                post_text: app.vue.new_post_text,
                username: response.data.username,
                email: response.data.email,
                liked: 0,
                like_id: -1,
                hover: false,
                likers: [],
                dislikers: [],
            });

            //traverse post list after an insertion
            for(let i = 0; i < app.vue.post_list.length; i++) {
                    if(app.vue.post_list[i].email === response.data.email) {
                        app.vue.post_list[i].liked = 1;
                        app.vue.post_list[i].like_id = response.data.id;
                        app.vue.post_list[i].likers.push(curr_user);
                        break;
                    }
            }

            app.enumerate(app.vue.post_list);
            app.cancel_post();
        });
    };
*/
    app.add_post = () => {
        // Function:  Inserting a new post.
        // First, need to initialize below->
        let new_post = {
            id: null,
            edit: true,
            editable: true,
            content: "",
            server_content: null,
            original_content: "",
            user: user_name,
            email: user_email,
            is_reply: null,
            
        };

        //Insert post at the top the list 
        app.data.posts = [new_post, ...app.data.posts]
        app.reindex(); // reenumerate roe with reindex
        
        // should print into console 
        console.log("Add post")
    };

    app.reply = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id !== null) {
            // A new reply.  Need to initialize it!
            let init_reply = {
                id: null,
                edit: true,
                editable: true,
                content: "",
                server_content: null,
                original_content: "",
                user: user_name,
                email: user_email,
                is_reply: p.id,
            };

           
            reply_list = []
            for(let k = 0; k < app.data.posts.length; k++) {
                reply_list.push(app.data.posts[k]) // should push app.data.post[k] to reply_list
                if(k == post_idx) {
                    reply_list.push(init_reply)
                }
            }

            app.data.posts = reply_list
            app.reindex()

            console.log("Reply to post")

            // Function: We need to insert it in the right place, and reindex
            // the posts.  
        }
    };

    app.do_delete = (post_idx) => {
        let p = app.vue.posts[post_idx];
        
        if (p.id === null) {
            
            // If the post has never been added to the server,
            // simply deletes it from the list of posts.
            app.data.posts.splice(post_idx, 1)
            app.reindex()
        } else {
            // Deletes the post on the server.
            // app.data.posts.splice(post_idx, 1)
            
            axios.post(delete_url, {id: p.id}).then((response) => {
            // The deletion went through on the server and locally
            // Splice deletes the element.
            
                app.vue.posts.splice(post_idx, 1);
                app.reindex();
            })
        }
    };
    //change_thumb(): Function to set the thumb rating
    //DEFINE:
    //thumb_choice is either 0 (up) or 1 (down) when rating
    app.change_thumb = (post_idx, thumb_choice) => { 
        let post = app.vue.posts[post_idx];
        let thumb_rating = 0; 
        // Change thumb_rating to represent the 3 states of thumb rating up/down
        //diff cases listed below 
        if(post.rating === 0) { //both thumb up and down are opaque 
            if(thumb_choice === 0) thumb_rating = 1; // thumb up is clicked
            else thumb_rating = 2; // thumb down is clicked
        }else if (post.rating === 1){ // only thumb down is opaque
            if(thumb_choice === 0) thumb_rating = 0;
            else thumb_rating = 2;
        }else{ // only thumb up is opaque
            if(thumb_choice === 0) thumb_rating = 1;
            else thumb_rating = 0;
        }
        axios.post(set_thumb_url, {post_id: post.id, rating: thumb_rating});
        app.vue.check_change_thumb_liked = true; // If we select thumbs up
        app.vue.check_change_thumb_disliked = true; // If we select thumbs down
        app.thumb_over(post_idx, thumb_rating);
        post.rating = thumb_rating;
    };

    app.thumb_out = (post_idx) => {
        let post = app.vue.posts[post_idx];
        post.show_liked_users = false;
        post.show_disliked_users = false;
    };
    app.thumb_over = (post_idx, thumb_choice) => {
        let post = app.vue.posts[post_idx];
        //If first hovering over post, want to use get_thumb
        if(post.asleep === true){
            app.vue.check_change_thumb_liked = post.asleep;
            app.vue.check_change_thumb_disliked = post.asleep;
            post.asleep = false; // Wake up post so that it obeys check_change_thumb rules below afterwards
        }

        // Show everyone who placed the thumb rating
        if(thumb_choice === 1){ //Show all who LIKED post
            if(app.vue.check_change_thumb_liked === true){ // use axios.get only change_thumb
                app.vue.check_change_thumb_liked = false;
                axios.get(get_thumb_url, {params: {"post_id": post.id, "rating": thumb_choice}})
                    .then((result) => {
                        post.display_liked_users = result.data.s;
                        if(post.display_liked_users != ""){
                            post.show_liked_users = true; //Need this here because you want to show liked users AFTER get_thumb finishes
                        }
                    });
            }
            //Goes through even if thumb rating has not changed
            else if (post.display_liked_users !== ""){ // Don't display empty string
                post.show_liked_users = true;
            }
        }
        if(thumb_choice === 2){ //Show all who DISLIKED post
            if(app.vue.check_change_thumb_disliked === true){
                app.vue.check_change_thumb_disliked = false;
                axios.get(get_thumb_url, {params: {"post_id": post.id, "rating": thumb_choice}})
                    .then((result) => {
                        post.display_disliked_users = result.data.s;
                        if(post.display_disliked_users != ""){
                            post.show_disliked_users = true;
                        }
                    });
            }
            else if (post.display_disliked_users !== ""){ //Check if no users have disliked post
                post.show_disliked_users = true;
            }
        }
    };

    app.like_post = function (post_idx, curr_user) {
        let post = app.vue.post_list[post_idx];

        // no like exists, add it
        if(post.liked == 0) {
            axios.post(
                add_like_url,
                {
                    is_like: true,
                    post: post.id,
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
            axios.post(
                delete_like_url,
                {id: post.like_id}
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
            axios.post(
                flip_like_url,
                {
                    id: post.like_id,
                    is_like: true,
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
            axios.post(
                add_like_url,
                {
                    is_like: false,
                    post: post.id,
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
            axios.post(
                flip_like_url,
                {
                    id: post.like_id,
                    is_like: false,
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
            axios.post(
                delete_like_url,
                {id: post.like_id}
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

    app.set_hover = function (p_idx, new_value) {
        app.vue.post_list[p_idx].hover = new_value;
    }

    app.cancel_post = function(){
        app.vue.add_mode = false;
        app.vue.new_post_text = "";
    };

/*
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
        });
    };

*/
    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
       
        like_post: app.like_post,
        dislike_post: app.dislike_post,
        get_liker_string: app.get_liker_string,
        set_hover: app.set_hover,
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
         // should deal with like and dislikes hopefully
         change_thumb: app.change_thumb,
         thumb_over: app.thumb_over,
         thumb_out: app.thumb_out,
        
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target-feed",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    /*
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(get_posts_url).then(function(result){
            let posts = result.data.posts;
            app.enumerate(posts);
            let likes = result.data.likes;
            //app.complete(posts);

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

            app.vue.post_list = posts;
        });
    };
*/
    // Call to the initializer.
// And this initializes it.
app.init = () => {
    // Posts need to be loaded from the server

    // Load the posts from the server instead.
    //  Then We set the posts later here.
    axios.get(posts_url).then((result) => {

        let posts = result.data.posts
        
        app.vue.posts = app.index(posts);
        posts.map((post) => {
            // alerts Vue to a new attribute of post
            // which should set rating to 0 originally
            Vue.set(post, "rating", 0);
        })
    }).then(() => {

        for(let post of app.vue.posts){
            axios.get(get_rating_url, {params: {"post_id": post.id}})
                .then((result) => {
                    Vue.set(post, "rating", result.data.rating);
                 });
        } 
    });
    console.log("app.init called...")

    // app.vue.posts = app.index(posts);
    };

    app.init();
};




// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
