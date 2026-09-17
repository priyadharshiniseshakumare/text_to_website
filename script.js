console.log("SCRIPT LOADED");
const button = document.querySelector("button");
const promptBox = document.querySelector("textarea");


button.addEventListener("click", async function () {

    const prompt = promptBox.value.trim();

    if (prompt === "") {
        alert("Please enter a website description!");
        return;
    }

    button.innerText = "Generating...";
    button.disabled = true;

    console.log("BUTTON CLICKED");
    console.log("Prompt:", prompt);

    try {

        const response = await fetch("/generate", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                prompt: prompt
            })
        });

        console.log("Response received");

        const data = await response.json();

        console.log("AI Response:", data);

        if (data.response) {

            let websiteCode = data.response;

            websiteCode = websiteCode
                .replace(/```html/gi, "")
                .replace(/```/g, "")
                .trim();

            let preview =
                document.getElementById("websitePreview");

            if (!preview) {

                preview = document.createElement("iframe");

                preview.id = "websitePreview";

                preview.style.width = "90%";
                preview.style.height = "600px";
                preview.style.marginTop = "30px";
                preview.style.border = "2px solid #ccc";
                preview.style.borderRadius = "10px";

                document.body.appendChild(preview);
            }

            preview.srcdoc = websiteCode;

        } else {

            alert("AI did not generate website.");

            console.log("Backend error:", data);
        }

    } catch (error) {

        console.error("ERROR:", error);

        alert("Something went wrong!");

    }

    button.innerText = "Generate Website";
    button.disabled = false;

});