def render_email_template(template):

    html = ""

    for block in template.blocks.all():

        if block.block_type == 'heading':

            html += f"""

            <h1>
                {block.content}
            </h1>

            """

        elif block.block_type == 'text':

            html += f"""

            <p>
                {block.content}
            </p>

            """

        elif block.block_type == 'button':

            html += f"""

            <a href="#"

               style="
               background:#0d6efd;
               color:white;
               padding:12px 20px;
               text-decoration:none;
               border-radius:6px;
               display:inline-block;">

               {block.content}

            </a>

            """

        elif block.block_type == 'image':

            html += f"""

            <img src="{block.content}"

                 style="
                 max-width:100%;
                 border-radius:10px;">

            """

    return html

def personalize_content(
    content,
    contact
):

    content = content.replace(
        "{{name}}",
        contact.name or "User"
    )

    content = content.replace(
        "{{email}}",
        contact.email
    )

    return content