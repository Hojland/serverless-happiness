intro_body = {
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "We all want you to be very happy. \n To help us, tell us. \n *How is your mood today?*"
			},
			"accessory": {
				"type": "image",
				"image_url": "https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg",
				"alt_text": "cute cat"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "radio_buttons",
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": ":star:",
								"emoji": True
							},
							"value": "star-1"
						},
						{
							"text": {
								"type": "plain_text",
								"text": ":star::star:",
								"emoji": True
							},
							"value": "star-2"
						},
						{
							"text": {
								"type": "plain_text",
								"text": ":star::star::star:",
								"emoji": True
							},
							"value": "star-3"
						},
						{
							"text": {
								"type": "plain_text",
								"text": ":star::star::star::star:",
								"emoji": True
							},
							"value": "star-4"
						},
						{
							"text": {
								"type": "plain_text",
								"text": ":star::star::star::star::star:",
								"emoji": True
							},
							"value": "star-5"
						}
					],
					"action_id": "actionId-0"
				}
			]
		}
	]
}

response_body = {
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "insert_markdown"
			}
		},
		{
			"type": "image",
			"image_url": "insert_picture",
			"alt_text": "inspiration"
		}
	]
}