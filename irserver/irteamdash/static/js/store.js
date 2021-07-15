const state = {
    apiUrl: API_BASE_URL,
    authHeader: null,
    toasts: [],
}

const mutations = {
    SET_AUTH_HEADER(state, token) {
        state.authHeader = {"Authorization": "Bearer "+token};
        localStorage.setItem("access_token", JSON.stringify(token));
    },
    UNSET_AUTH_HEADER(state) {
        state.authHeader = null;
        localStorage.removeItem("access_token");
    },
    CREATE_TOAST(state, toast) {
        state.toasts.push(toast)
    },
    REMOVE_TOAST(state, id) {
        state.toasts = state.toasts.filter(t => t.id !== id)
    },
};

let maxToastId = 0;

const actions = {
    setAuthInfo(context, json) {
        context.commit("SET_AUTH_HEADER", json.access_token);
    },
    unsetAuthInfo(context) {
        context.commit("UNSET_AUTH_HEADER");
    },
    initAuthInfo(context) {
        var accessToken = JSON.parse(localStorage.getItem("access_token"));
        if (accessToken != null) {
            context.commit("SET_AUTH_HEADER", accessToken);
        }
    },
    createToast(context, toast) {
        // handle non-string input such as errors
        // errors from processing successful responses can end up here
        if (!("content" in toast)) {
            console.error(toast);
            return
        }
        const id = ++maxToastId;
        toast.id = id;
        context.commit("CREATE_TOAST", toast);
        setTimeout(() => {
            context.commit("REMOVE_TOAST", id);
        }, 5000)
    },
};

const getters = {
    getApiUrl(state) {
        return state.apiUrl;
    },
    getAuthHeader(state) {
        return state.authHeader;
    },
    getToasts(stats) {
        return state.toasts;
    },
    isLoggedIn(state, getters) {
        if (getters.getAuthHeader === null) {
            return false;
        }
        return true;
    },
};

const store = new Vuex.Store({
    state,
    mutations,
    actions,
    getters,
});

// initialize the store prior to instantiating the app to ensure
// the router.beforeEach check gets the proper isLoggedIn value
store.dispatch("initAuthInfo");
