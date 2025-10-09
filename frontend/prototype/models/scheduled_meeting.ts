import {BlockerPreview} from "../models/blockers"

export class Time {
    hour: number
    minute: number
    is_am: boolean
}

export class MeetingTimes {
    start_time: Time
    end_time: Time
    duration: Time
}

export class ScheduledMeeting {
    associated_blockers: BlockerPreview[]
    meeting_dates: string[]
    meeting_times: MeetingTimes[]

    description: string

    
}