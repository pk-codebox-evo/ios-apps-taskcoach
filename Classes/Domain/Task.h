//
//  Task.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "DomainObject.h"

@interface Task : DomainObject
{
	NSString *description;
	NSString *startDate;
	NSString *dueDate;
	NSString *completionDate;
}

@property (nonatomic, retain) NSString *description;
@property (nonatomic, retain) NSString *startDate;
@property (nonatomic, retain) NSString *dueDate;
@property (nonatomic, retain) NSString *completionDate;

- initWithId:(NSInteger)ID name:(NSString *)name status:(NSInteger)status description:(NSString *)description startDate:(NSString *)startDate dueDate:(NSString *)dueDate completionDate:(NSString *)completionDate;

@end
