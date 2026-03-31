from telethon import events, types, functions

reasons = [
    types.InputReportReasonChildAbuse(),
    types.InputReportReasonCopyright(),
    types.InputReportReasonFake(),
    types.InputReportReasonPornography(),
    types.InputReportReasonSpam(),
    types.InputReportReasonViolence(),
    types.InputReportReasonOther(),
    types.InputReportReasonCopyright(),
    types.InputReportReasonIllegalDrugs(),
    types.InputReportReasonGeoIrrelevant()
]


def a(client):
    @client.on(events.NewMessage(pattern=r"\.report", outgoing=True))
    async def _(event):
        reported_actions = set()

        chat_id = event.chat_id
        if chat_id in reported_actions:
            return await event.edit("<b>Действие уже было выполнено ранее.</b>", parse_mode='html')

        args = event.message.text.split(' ')
        times = 1

        if len(args) > 1 and args[1].isdigit():
            times = int(args[1])

        for _ in range(times):
            for reason in reasons:
                try:
                    await client(
                        functions.account.ReportPeerRequest(
                            peer=event.peer_id,
                            reason=reason,
                            message=''
                        )
                    )

                    reason_text = str(reason).replace('InputReportReason', '').replace('()', '')
                    await event.edit(f'Жалоба {reason_text} отправлена!')
                except Exception as e:
                    print(e)

        reported_actions.add(chat_id)
        await event.edit(f'<b>Жалобы ({times * len(reasons)}) успешно отправлены!</b>', parse_mode='html')
