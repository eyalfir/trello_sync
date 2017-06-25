# trello_sync

simple utility to sync a Trello board to YAML file

## Setup

add this JSON file to your HOME directory, under the name .trello:

```
        {
                "key": "YOUR TRELLO KEY",
                "token":"YOUR TRELLO TOKEN",
                "board": "BOARD ID",
                "filename": "FILENAME TO SYNC"
        }
```

## Getting a token:

Sign-in to trello.com as the user you want to use for trello_cli.

Get API key (open this link in a web browser):

    https://trello.com/1/appKey/generate

The top field contains your Developer API Key.  Use it to replace **YOUR TRELLO KEY**.

Next, get a member token. You will need to replace **YOUR_API_KEY** in the link below with the API key obtained in the previous step.

    https://trello.com/1/authorize?key=YOUR_API_KEY&name=trello_sync&expiration=never&response_type=token&scope=read,write

Use the result to replace **YOUR TRELLO TOKEN** in the .trello file.


## Pro tip

Add this to your .vimrc to have VIM automatically sync the board file:

    autocmd! BufWritePost *board.yml !cp ~/board.yml /tmp/board.yml.backup && trello_sync update 2>> /tmp/sync.log && trello_sync fetch > ~/board.yml

## Thanks

Thanks to @weavenet and his [trello_cli](https://github.com/weavenet/trello_cli) repository from which parts of this README file was created.
