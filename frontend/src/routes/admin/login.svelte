<script lang="ts">
    let username: string
    let password: string
    let msg = ""

    async function login(e: MouseEvent) {
        await fetch("/api/admin/login", {
            method: "post",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new  URLSearchParams({
                username: username,
                password: password
            })
        }).then(r => {
            if(r.status == 204) document.location.href = document.location.origin+"/admin"
            else {
                msg = "Unknown user"
                document.getElementById("msg").style.display = "block"
            }
        })
    }
</script>

<form>
    <p id="msg" style="display: none">{msg}</p>
    <input name="username" bind:value={username}>
    <input name="password" type="password" bind:value={password}>
    <button type="submit" on:click|preventDefault="{login}">Login</button>
</form>